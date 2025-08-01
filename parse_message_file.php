<?php

/**
 * Detects the character encoding of a file by reading its Byte Order Mark (BOM).
 *
 * @param resource|string $infile A file path or a stream resource.
 * @param bool $closefp If true and $infile is a path, the file handle will be closed.
 * @return string|false The detected encoding name (e.g., "UTF-8") or false on failure.
 */
function get_file_encoding($infile, bool $closefp = true)
{
    $fp = null;
    $is_path = is_string($infile);

    if ($is_path) {
        if (!file_exists($infile)) {
            return false;
        }
        $fp = @fopen($infile, 'rb');
        if ($fp === false) {
            return false;
        }
    } elseif (is_resource($infile) && get_resource_type($infile) === 'stream') {
        $fp = $infile;
    } else {
        return false; // Invalid input type
    }

    // Default encoding if no BOM is found
    $file_encoding = "UTF-8";

    // The logic follows the original Python script, checking for BOMs of
    // different lengths. A later, more specific match will override an earlier one.
    fseek($fp, 0, SEEK_SET);
    $bom2 = fread($fp, 2);
    if ($bom2 === hex2bin("fffe")) $file_encoding = "UTF-16LE";
    elseif ($bom2 === hex2bin("feff")) $file_encoding = "UTF-16BE";

    fseek($fp, 0, SEEK_SET);
    $bom3 = fread($fp, 3);
    if ($bom3 === hex2bin("efbbbf")) $file_encoding = "UTF-8";
    elseif ($bom3 === hex2bin("0efeff")) $file_encoding = "SCSU";

    fseek($fp, 0, SEEK_SET);
    $bom4 = fread($fp, 4);
    if ($bom4 === hex2bin("fffe0000")) $file_encoding = "UTF-32LE";
    elseif ($bom4 === hex2bin("0000feff")) $file_encoding = "UTF-32BE";
    elseif ($bom4 === hex2bin("dd736673")) $file_encoding = "UTF-EBCDIC";
    elseif (in_array($bom4, [hex2bin("2b2f7638"), hex2bin("2b2f7639"), hex2bin("2b2f762b"), hex2bin("2b2f762f")])) {
        $file_encoding = "UTF-7";
    }

    // Reset pointer to the beginning of the file for subsequent operations
    fseek($fp, 0, SEEK_SET);

    if ($closefp && $is_path) {
        fclose($fp);
    }

    return $file_encoding;
}

/**
 * Detects encoding from a string by treating it as an in-memory file.
 *
 * @param string $instring The input string to check.
 * @return string|false The detected encoding name or false on failure.
 */
function get_file_encoding_from_string(string $instring)
{
    $stream = fopen('php://memory', 'r+');
    fwrite($stream, $instring);
    rewind($stream); // Go to the beginning of the stream

    $encoding = get_file_encoding($stream, false); // Pass stream, don't close it inside

    fclose($stream); // Close the memory stream
    return $encoding;
}

function validate_service_data($service, $schema) {
    if (!is_array($service)) {
        return array(false, "Service must be an array/dictionary");
    }

    if (!isset($schema['Service'])) {
        return array(false, "Schema missing 'Service' root");
    }
    $sroot = $schema['Service'];

    // Helper type tester
    $is_type = function($value, $expected) {
        switch ($expected) {
            case "int":       return is_int($value);
            case "string":    return is_string($value);
            case "list":      return is_array($value); // we assume normal PHP arrays as lists
            case "dict":      return is_array($value); // PHP arrays can be dicts as well
            case "multiline": return is_string($value);
            default:          return true; // unknown => accept or reject
        }
    };

    $fail = function($msg) { return array(false, $msg); };
    $ok   = function()     { return array(true, "OK"); };

    // 1) Required keys
    if (isset($sroot['required_keys']) && is_array($sroot['required_keys'])) {
        foreach ($sroot['required_keys'] as $key) {
            if (!array_key_exists($key, $service)) {
                return $fail("Missing required key '$key' in service");
            }
        }
    }

    // 2) Type checks for top-level keys
    $types = isset($sroot['types']) && is_array($sroot['types']) ? $sroot['types'] : array();
    foreach ($service as $key => $value) {
        if (isset($types[$key]) && !$is_type($value, $types[$key])) {
            return $fail("Key '$key' should be a ".$types[$key]." but got ".gettype($value));
        }
    }

    // 3) Categories
    $categories = isset($service['Categories']) ? $service['Categories'] : array();
    $category_ids_by_type = array();

    $cat_schema = isset($sroot['sections']['Categories']) ? $sroot['sections']['Categories'] : array();
    $cat_keys   = isset($cat_schema['keys'])  ? $cat_schema['keys']  : array();
    $cat_types  = isset($cat_schema['types']) ? $cat_schema['types'] : array();

    foreach ($categories as $cat) {
        foreach ($cat_keys as $ck) {
            if (!isset($cat[$ck])) {
                return $fail("Category missing required key '$ck'");
            }
            if (isset($cat_types[$ck]) && !$is_type($cat[$ck], $cat_types[$ck])) {
                return $fail("Category key '$ck' should be ".$cat_types[$ck]);
            }
        }

        // your parser adds "Type" from the Kind field
        $ctype = isset($cat['Type']) ? $cat['Type'] : '';
        if ($ctype !== '') {
            if (!isset($category_ids_by_type[$ctype])) {
                $category_ids_by_type[$ctype] = array();
            }
            $category_ids_by_type[$ctype][$cat['ID']] = true;
        }
    }

    // 4) Users
    $users = isset($service['Users']) ? $service['Users'] : array();
    foreach ($users as $uid => $uinfo) {
        // PHP arrays have string keys possible; assume user IDs should be ints
        if (!is_int($uid)) {
            return $fail("User ID '$uid' is not an int");
        }
        if (!isset($uinfo['Name']) || !isset($uinfo['Handle'])) {
            return $fail("User $uid missing Name or Handle");
        }
    }

    // 5) MessageThreads
    $threads = isset($service['MessageThreads']) ? $service['MessageThreads'] : array();
    $mt_schema = isset($sroot['sections']['MessageThreads']) ? $sroot['sections']['MessageThreads'] : array();
    $mt_types  = isset($mt_schema['types']) ? $mt_schema['types'] : array();

    $mp_schema = isset($mt_schema['MessagePosts']) ? $mt_schema['MessagePosts'] : array();
    $mp_types  = isset($mp_schema['types']) ? $mp_schema['types'] : array();
    $mp_keys   = isset($mp_schema['keys']) ? $mp_schema['keys'] : array();

    foreach ($threads as $tidx => $thread) {
        if (!isset($thread['Thread']) || !is_int($thread['Thread'])) {
            return $fail("Thread $tidx missing or invalid 'Thread' ID");
        }

        foreach ($thread as $k => $v) {
            if (isset($mt_types[$k]) && !$is_type($v, $mt_types[$k])) {
                return $fail("Thread ".$thread['Thread']." key '$k' should be ".$mt_types[$k]);
            }
        }

        // Collect post IDs
        $post_ids = array();
        $messages = isset($thread['Messages']) ? $thread['Messages'] : array();

        // minimal required per message
        $mp_required = array();
        foreach ($mp_keys as $k) {
            if (in_array($k, array("Post", "Author", "Date", "Time"), true)) {
                $mp_required[] = $k;
            }
        }

        foreach ($messages as $msg) {
            foreach ($mp_required as $rk) {
                if (!isset($msg[$rk])) {
                    return $fail("Thread ".$thread['Thread']." post missing required key '$rk'");
                }
            }
            foreach ($msg as $mk => $mv) {
                if (isset($mp_types[$mk]) && !$is_type($mv, $mp_types[$mk])) {
                    $postid = isset($msg['Post']) ? $msg['Post'] : 'UNKNOWN';
                    return $fail("Thread ".$thread['Thread']." Post $postid: key '$mk' should be ".$mp_types[$mk]);
                }
            }
            if (isset($msg['Post']) && is_int($msg['Post'])) {
                $post_ids[$msg['Post']] = true;
            }
        }

        // Validate nested refs and author IDs
        foreach ($messages as $msg) {
            $postid = isset($msg['Post']) && is_int($msg['Post']) ? $msg['Post'] : 'UNKNOWN';

            if (isset($msg['Nested']) && is_int($msg['Nested'])) {
                if ($msg['Nested'] != 0 && !isset($post_ids[$msg['Nested']])) {
                    return $fail("Thread ".$thread['Thread']." Post $postid: Nested references non-existent Post ".$msg['Nested']);
                }
            }
            if (isset($msg['AuthorID']) && is_int($msg['AuthorID'])) {
                if (!isset($users[$msg['AuthorID']])) {
                    return $fail("Thread ".$thread['Thread']." Post $postid: AuthorID ".$msg['AuthorID']." not found in Users");
                }
            }
            if (isset($msg['Polls']) && !is_array($msg['Polls'])) {
                return $fail("Thread ".$thread['Thread']." Post $postid: 'Polls' must be a list");
            }
        }
    }

    // 6) Cross-check category InSub references
    foreach ($categories as $cat) {
        $ctype = isset($cat['Type']) ? $cat['Type'] : '';
        $insub = isset($cat['InSub']) ? $cat['InSub'] : 0;
        if ($ctype !== '' && $insub != 0) {
            if (!isset($category_ids_by_type[$ctype][$insub])) {
                return $fail("Category ID ".$cat['ID']." InSub=$insub not found among '".$ctype."' IDs");
            }
        }
    }

    return $ok();
}

function validate_services($service, $schema) {
    return validate_service_data($service, $schema)
}

function validate_services_from_file($filename, $schema_or_path) {
    // Load schema
    if (is_string($schema_or_path) && file_exists($schema_or_path)) {
        $schema_content = file_get_contents($schema_or_path);
        $schema = json_decode($schema_content, true);
        if ($schema === null) {
            return array(false, "Failed to decode JSON schema: " . json_last_error_msg());
        }
    } else {
        $schema = $schema_or_path; // assume it's already an array
        if (!is_array($schema)) {
            return array(false, "Schema is not an array");
        }
    }

    // Parse the archive
    try {
        $services = parse_file($filename);
    } catch (Exception $e) {
        return array(false, "Failed to parse file: " . $e->getMessage());
    }

    // Validate all services
    return validate_services($services, $schema);
}

/**
 * Opens a file, transparently decompressing it based on its extension.
 * NOTE: This uses PHP's stream wrappers, which is very efficient.
 *
 * @param string $filename Path to the file.
 * @return resource|false A file handle resource on success, or false on failure.
 */
function open_compressed_file(string $filename)
{
    if (!file_exists($filename)) {
        trigger_error("open_compressed_file({$filename}): Failed to open stream: No such file or directory", E_USER_WARNING);
        return false;
    }

    if (str_ends_with($filename, '.gz')) {
        // Use the zlib stream wrapper
        return fopen('compress.zlib://' . $filename, 'r');
    } elseif (str_ends_with($filename, '.bz2')) {
        // Use the bzip2 stream wrapper
        return fopen('compress.bzip2://' . $filename, 'r');
    } else {
        // Open as a regular, uncompressed file
        return fopen($filename, 'r');
    }
}

/**
 * Saves data to a file, applying compression based on the file extension.
 *
 * @param string $data The string data to save.
 * @param string $filename The path where the file will be saved.
 * @return int|false The number of bytes written, or false on failure.
 */
function save_compressed_file(string $data, string $filename)
{
    if (str_ends_with($filename, '.gz')) {
        $compressed_data = gzencode($data);
        if ($compressed_data === false) {
            return false; // Gzip encoding failed
        }
        return file_put_contents($filename, $compressed_data);
    } elseif (str_ends_with($filename, '.bz2')) {
        $compressed_data = bzcompress($data);
        if (is_int($compressed_data)) {
            // bzcompress returns an error code (int) on failure
            return false;
        }
        return file_put_contents($filename, $compressed_data);
    } else {
        // Save as a regular, uncompressed file
        return file_put_contents($filename, $data);
    }
}

/**
 * Utility to validate that a given value is a non-negative integer.
 *
 * @param string $value The string value to validate.
 * @param string $key The key associated with the value, for error reporting.
 * @param int $line_number The line number for error reporting.
 * @return int The validated non-negative integer.
 * @throws \ValueError If the value is not a valid integer or is negative.
 */
function validate_non_negative_integer(string $value, string $key, int $line_number): int
{
    // filter_var is a strict way to validate if a string is an integer.
    // It returns false if the string contains non-numeric characters (except a leading sign).
    $int_value = filter_var($value, FILTER_VALIDATE_INT);

    if ($int_value === false) {
        throw new \ValueError(
            sprintf("Invalid integer '%s' for key '%s' on line %d", $value, $key, $line_number)
        );
    }

    // Now that we have a valid integer, check if it's negative.
    if ($int_value < 0) {
        throw new \ValueError(
            sprintf("Negative value '%s' for key '%s' on line %d", $value, $key, $line_number)
        );
    }

    return $int_value;
}

/**
 * Parses a line in the format 'key: value' and returns the key and value.
 *
 * @param string $line The line to parse.
 * @return array An array of [key, value] or [null, null] if parsing fails.
 */
function parse_line(string $line): array
{
    // The limit parameter '2' ensures we only split on the first colon
    $parts = explode(':', $line, 2);

    if (count($parts) === 2) {
        return [trim($parts[0]), trim($parts[1])];
    }

    return [null, null];
}

/**
 * Note: The following helper functions are assumed to exist and are required for this code to run.
 * They are the PHP equivalents of the helper functions used in the original Python script.
 *
 * function parse_file(string $filename, bool $validate_only, bool $verbose): array;
 * function parse_line(string $line): array; // Should return an array like [$key, $value]
 * function validate_non_negative_integer($value, string $field_name, int $line_number): int;
 */

function parse_lines(array $lines, bool $validate_only = false, bool $verbose = false): array
{
    $services = [];
    $current_service = null;
    $in_section = [
        'user_list' => false,
        'message_list' => false,
        'message_thread' => false,
        'user_info' => false,
        'message_post' => false,
        'extrafields_body' => false,
        'bio_body' => false,
        'signature_body' => false,
        'message_body' => false,
        'comment_section' => false,
        'include_service' => false,
        'include_users' => false,
        'include_messages' => false,
        'category_list' => false,
        'description_body' => false,
        'include_categories' => false,
        'categorization_list' => false,
        'info_body' => false,
        'poll_list' => false,
        'poll_body' => false,
    ];
    $include_files = [];
    $user_id = null;
    $current_bio = null;
    $current_message = null;
    $current_thread = null;
    $current_category = null;
    $current_info = null;
    $current_poll = null;
    $current_polls = [];
    $categorization_values = ['Categories' => [], 'Forums' => []];
    $category_ids = ['Categories' => [], 'Forums' => []];
    $post_id = 1;

    $parse_include_files = function (array $file_list) use ($validate_only, $verbose): array {
        $included_services = [];
        foreach ($file_list as $include_file) {
            $included_services = array_merge($included_services, parse_file($include_file, $validate_only, $verbose));
        }
        return $included_services;
    };

    $parse_include_users = function (array $file_list) use ($validate_only, $verbose): array {
        $users = [];
        foreach ($file_list as $include_file) {
            $included_users = parse_file($include_file, $validate_only, $verbose);
            foreach ($included_users as $service) {
                $users = array_merge($users, $service['Users']);
            }
        }
        return $users;
    };

    $parse_include_messages = function (array $file_list) use ($validate_only, $verbose): array {
        $messages = [];
        foreach ($file_list as $include_file) {
            $included_messages = parse_file($include_file, $validate_only, $verbose);
            foreach ($included_messages as $service) {
                $messages = array_merge($messages, $service['MessageThreads']);
            }
        }
        return $messages;
    };

    $parse_include_categories = function (array $file_list) use ($validate_only, $verbose): array {
        $categories = [];
        foreach ($file_list as $include_file) {
            $included_categories = parse_file($include_file, $validate_only, $verbose);
            foreach ($included_categories as $service) {
                $categories = array_merge($categories, $service['Categories']);
            }
        }
        return $categories;
    };

    try {
        $lineNumber = 0;
        foreach ($lines as $line) {
            $lineNumber++;
            $line = trim($line);

            if ($line === "--- Include Service Start ---") {
                $in_section['include_service'] = true;
                $include_files = [];
                if ($verbose) echo "Line {$lineNumber}: {$line} (Starting include service section)\n";
                continue;
            } elseif ($line === "--- Include Service End ---") {
                $in_section['include_service'] = false;
                if ($verbose) echo "Line {$lineNumber}: {$line} (Ending include service section)\n";
                $services = array_merge($services, $parse_include_files($include_files));
                continue;
            } elseif ($in_section['include_service']) {
                $include_files[] = $line;
                if ($verbose) echo "Line {$lineNumber}: {$line} (Including file for service)\n";
                continue;
            } elseif ($line === "--- Include Users Start ---") {
                $in_section['include_users'] = true;
                $include_files = [];
                if ($verbose) echo "Line {$lineNumber}: {$line} (Starting include users section)\n";
                continue;
            } elseif ($line === "--- Include Users End ---") {
                $in_section['include_users'] = false;
                if ($verbose) echo "Line {$lineNumber}: {$line} (Ending include users section)\n";
                if ($current_service) {
                    $current_service['Users'] = array_merge($current_service['Users'], $parse_include_users($include_files));
                }
                continue;
            } elseif ($in_section['include_users']) {
                $include_files[] = $line;
                if ($verbose) echo "Line {$lineNumber}: {$line} (Including file for users)\n";
                continue;
            } elseif ($line === "--- Include Messages Start ---") {
                $in_section['include_messages'] = true;
                $include_files = [];
                if ($verbose) echo "Line {$lineNumber}: {$line} (Starting include messages section)\n";
                continue;
            } elseif ($line === "--- Include Messages End ---") {
                $in_section['include_messages'] = false;
                if ($verbose) echo "Line {$lineNumber}: {$line} (Ending include messages section)\n";
                if ($current_service) {
                    $current_service['MessageThreads'] = array_merge($current_service['MessageThreads'], $parse_include_messages($include_files));
                }
                continue;
            } elseif ($in_section['include_messages']) {
                $include_files[] = $line;
                if ($verbose) echo "Line {$lineNumber}: {$line} (Including file for messages)\n";
                continue;
            } elseif ($line === "--- Include Categories Start ---") {
                $in_section['include_categories'] = true;
                $include_files = [];
                if ($verbose) echo "Line {$lineNumber}: {$line} (Starting include categories section)\n";
                continue;
            } elseif ($line === "--- Include Categories End ---") {
                $in_section['include_categories'] = false;
                if ($verbose) echo "Line {$lineNumber}: {$line} (Ending include categories section)\n";
                if ($current_service) {
                    $current_service['Categories'] = array_merge($current_service['Categories'], $parse_include_categories($include_files));
                    foreach ($current_service['Categories'] as &$category) {
                        $kind_split = explode(",", $category['Kind'] ?? '');
                        $category['Type'] = isset($kind_split[0]) ? trim($kind_split[0]) : "";
                        $category['Level'] = isset($kind_split[1]) ? trim($kind_split[1]) : "";
                        $category_ids[$category['Type']][] = $category['ID'];
                    }
                    unset($category); // Unset reference
                }
                continue;
            } elseif ($in_section['include_categories']) {
                $include_files[] = $line;
                if ($verbose) echo "Line {$lineNumber}: {$line} (Including file for categories)\n";
                continue;
            } elseif ($line === "--- Start Archive Service ---") {
                $current_service = ['Users' => [], 'MessageThreads' => [], 'Categories' => [], 'Interactions' => [], 'Categorization' => [], 'Info' => ''];
                if ($verbose) echo "Line {$lineNumber}: {$line} (Starting new archive service)\n";
                continue;
            } elseif ($line === "--- End Archive Service ---") {
                $services[] = $current_service;
                $current_service = null;
                if ($verbose) echo "Line {$lineNumber}: {$line} (Ending archive service)\n";
                continue;
            } elseif ($line === "--- Start Comment Section ---") {
                $in_section['comment_section'] = true;
                if ($verbose) echo "Line {$lineNumber}: {$line} (Starting comment section)\n";
                continue;
            } elseif ($line === "--- End Comment Section ---") {
                $in_section['comment_section'] = false;
                if ($verbose) echo "Line {$lineNumber}: {$line} (Ending comment section)\n";
                continue;
            } elseif ($in_section['comment_section']) {
                if ($verbose) echo "Line {$lineNumber}: {$line} (Comment)\n";
                continue;
            } elseif ($line === "--- Start Category List ---") {
                $in_section['category_list'] = true;
                $current_category = [];
                if ($verbose) echo "Line {$lineNumber}: {$line} (Starting category list)\n";
                continue;
            } elseif ($line === "--- End Category List ---") {
                $in_section['category_list'] = false;
                if ($current_category) {
                    $kind_split = explode(",", $current_category['Kind'] ?? '');
                    $current_category['Type'] = isset($kind_split[0]) ? trim($kind_split[0]) : "";
                    $current_category['Level'] = isset($kind_split[1]) ? trim($kind_split[1]) : "";
                    if (!array_key_exists($current_category['Type'], $categorization_values)) {
                        throw new \Exception(sprintf("Invalid 'Type' value '%s' on line %d. Expected one of %s.", $current_category['Type'], $lineNumber, implode(', ', array_keys($categorization_values))));
                    }
                    if ($current_category['InSub'] != 0 && !in_array($current_category['InSub'], $category_ids[$current_category['Type']])) {
                        throw new \Exception(sprintf("InSub value '%s' on line %d does not match any existing ID values.", $current_category['InSub'], $lineNumber));
                    }
                    $current_service['Categories'][] = $current_category;
                    $category_ids[$current_category['Type']][] = $current_category['ID'];
                }
                $current_category = null;
                if ($verbose) echo "Line {$lineNumber}: {$line} (Ending category list)\n";
                continue;
            } elseif ($line === "--- Start Categorization List ---") {
                $in_section['categorization_list'] = true;
                $current_service['Categorization'] = [];
                if ($verbose) echo "Line {$lineNumber}: {$line} (Starting categorization list)\n";
                continue;
            } elseif ($line === "--- End Categorization List ---") {
                $in_section['categorization_list'] = false;
                if ($verbose) echo "Line {$lineNumber}: {$line} (Ending categorization list)\n";
                $categorization_values = $current_service['Categorization'];
                continue;
            } elseif ($line === "--- Start Info Body ---") {
                $in_section['info_body'] = true;
                if ($current_service) {
                    $current_info = [];
                    if ($verbose) echo "Line {$lineNumber}: {$line} (Starting info body)\n";
                }
                continue;
            } elseif ($line === "--- End Info Body ---") {
                $in_section['info_body'] = false;
                if ($current_service && $current_info !== null) {
                    $current_service['Info'] = implode("\n", $current_info);
                    $current_info = null;
                    if ($verbose) echo "Line {$lineNumber}: {$line} (Ending info body)\n";
                }
                continue;
            } elseif ($in_section['info_body']) {
                if ($current_service && $current_info !== null) {
                    $current_info[] = $line;
                }
                if ($verbose) echo "Line {$lineNumber}: {$line}\n";
                continue;
            } elseif ($line === "--- Start Poll List ---") {
                $in_section['poll_list'] = true;
                $current_polls = [];
                if ($verbose) echo "Line {$lineNumber}: {$line} (Starting poll list)\n";
                continue;
            } elseif ($line === "--- End Poll List ---") {
                $in_section['poll_list'] = false;
                if ($current_message) {
                    $current_message['Polls'] = $current_polls;
                }
                if ($verbose) echo "Line {$lineNumber}: {$line} (Ending poll list)\n";
                continue;
            } elseif ($in_section['poll_list'] && $line === "--- Start Poll Body ---") {
                $in_section['poll_body'] = true;
                $current_poll = [];
                if ($verbose) echo "Line {$lineNumber}: {$line} (Starting poll body)\n";
                continue;
            } elseif ($in_section['poll_body'] && $line === "--- End Poll Body ---") {
                $in_section['poll_body'] = false;
                if ($current_poll !== null) {
                    $current_polls[] = $current_poll;
                    $current_poll = null;
                }
                if ($verbose) echo "Line {$lineNumber}: {$line} (Ending poll body)\n";
                continue;
            } elseif ($in_section['poll_body']) {
                list($key, $value) = parse_line($line);
                if ($key && $current_poll !== null) {
                    if (in_array($key, ['Answers', 'Results', 'Percentage'])) {
                        $current_poll[$key] = array_map('trim', explode(',', $value));
                    } else {
                        $current_poll[$key] = $value;
                    }
                }
                continue;
            }

            if ($current_service !== null) {
                list($key, $value) = parse_line($line);
                if ($key === "Entry") {
                    $current_service['Entry'] = validate_non_negative_integer($value, "Entry", $lineNumber);
                } elseif ($key === "Service") {
                    $current_service['Service'] = $value;
                } elseif ($key === "ServiceType") {
                    $current_service['ServiceType'] = $value;
                } elseif ($key === "ServiceLocation") {
                    $current_service['ServiceLocation'] = $value;
                } elseif ($key === "TimeZone") {
                    $current_service['TimeZone'] = $value;
                } elseif ($key === "Categories") {
                    $current_service['Categorization']['Categories'] = array_map('trim', explode(",", $value));
                    if ($verbose) echo "Line {$lineNumber}: Categories set to " . implode(', ', $current_service['Categorization']['Categories']) . "\n";
                } elseif ($key === "Forums") {
                    $current_service['Categorization']['Forums'] = array_map('trim', explode(",", $value));
                    if ($verbose) echo "Line {$lineNumber}: Forums set to " . implode(', ', $current_service['Categorization']['Forums']) . "\n";
                } elseif ($line === "--- Start Description Body ---" && $in_section['category_list']) {
                    $in_section['description_body'] = true;
                    $_desc_lines = [];
                    continue;
                } elseif ($line === "--- End Description Body ---" && $in_section['category_list']) {
                    $in_section['description_body'] = false;
                    $current_category['Description'] = implode("\n", $_desc_lines);
                    unset($_desc_lines);
                    continue;
                } elseif ($in_section['description_body'] && $in_section['category_list']) {
                    $_desc_lines[] = $line;
                    continue;
                } elseif ($in_section['category_list']) {
                    if ($key === "Kind") $current_category['Kind'] = $value;
                    elseif ($key === "ID") $current_category['ID'] = validate_non_negative_integer($value, "ID", $lineNumber);
                    elseif ($key === "InSub") $current_category['InSub'] = validate_non_negative_integer($value, "InSub", $lineNumber);
                    elseif ($key === "Headline") $current_category['Headline'] = $value;
                    elseif ($key === "Description") $current_category['Description'] = $value;
                } elseif ($line === "--- Start User List ---") {
                    $in_section['user_list'] = true;
                    if ($verbose) echo "Line {$lineNumber}: {$line} (Starting user list)\n";
                    continue;
                } elseif ($line === "--- End User List ---") {
                    $in_section['user_list'] = false;
                    if ($verbose) echo "Line {$lineNumber}: {$line} (Ending user list)\n";
                    continue;
                } elseif ($line === "--- Start User Info ---") {
                    $in_section['user_info'] = true;
                    if ($verbose) echo "Line {$lineNumber}: {$line} (Starting user info)\n";
                    continue;
                } elseif ($line === "--- End User Info ---") {
                    $in_section['user_info'] = false;
                    $user_id = null;
                    if ($verbose) echo "Line {$lineNumber}: {$line} (Ending user info)\n";
                    continue;
                } elseif ($line === "--- Start Message List ---") {
                    $in_section['message_list'] = true;
                    if ($verbose) echo "Line {$lineNumber}: {$line} (Starting message list)\n";
                    continue;
                } elseif ($line === "--- End Message List ---") {
                    $in_section['message_list'] = false;
                    if ($verbose) echo "Line {$lineNumber}: {$line} (Ending message list)\n";
                    continue;
                } elseif ($line === "--- Start Message Thread ---") {
                    $in_section['message_thread'] = true;
                    $current_thread = ['Title' => '', 'Messages' => []];
                    $post_id = 1;
                    if ($verbose) echo "Line {$lineNumber}: {$line} (Starting message thread)\n";
                    continue;
                } elseif ($line === "--- End Message Thread ---") {
                    $in_section['message_thread'] = false;
                    $current_service['MessageThreads'][] = $current_thread;
                    $current_thread = null;
                    if ($verbose) echo "Line {$lineNumber}: {$line} (Ending message thread)\n";
                    continue;
                } elseif ($line === "--- Start Message Post ---") {
                    $in_section['message_post'] = true;
                    $current_message = [];
                    if ($verbose) echo "Line {$lineNumber}: {$line} (Starting message post)\n";
                    continue;
                } elseif ($line === "--- End Message Post ---") {
                    $in_section['message_post'] = false;
                    if ($current_message) {
                        $current_thread['Messages'][] = $current_message;
                    }
                    $current_message = null;
                    if ($verbose) echo "Line {$lineNumber}: {$line} (Ending message post)\n";
                    continue;
				} elseif ($line === "--- Start Message Body ---") {
					if ($current_message !== null) {
						$current_message['Message'] = [];
						$in_section['message_body'] = true;
						if ($verbose) echo "Line {$lineNumber}: Starting message body\n";
					}
					continue;
				} elseif ($line === "--- End Message Body ---") {
					if ($current_message !== null && isset($current_message['Message'])) {
						$current_message['Message'] = implode("\n", $current_message['Message']);
						$in_section['message_body'] = false;
						if ($verbose) echo "Line {$lineNumber}: Ending message body\n";
					}
					continue;
				} elseif ($in_section['message_body'] && $current_message !== null && isset($current_message['Message'])) {
					 $current_message['Message'][] = $line;
					 if ($verbose) echo "Line {$lineNumber}: Adding to message body: {$line}\n";
					 continue;
                } elseif ($in_section['message_list'] && $key === "Interactions") {
                    $current_service['Interactions'] = array_map('trim', explode(",", $value));
                    if ($verbose) echo "Line {$lineNumber}: Interactions set to " . implode(', ', $current_service['Interactions']) . "\n";
                } elseif ($in_section['message_list'] && $key === "Status") {
                    $current_service['Status'] = array_map('trim', explode(",", $value));
                    if ($verbose) echo "Line {$lineNumber}: Status set to " . implode(', ', $current_service['Status']) . "\n";
                } elseif ($key === "Info") {
                    $current_info = [];
                    $in_section['info_body'] = true;
                    if ($verbose) echo "Line {$lineNumber}: {$line} (Starting info body)\n";
                } elseif ($in_section['user_list'] && $in_section['user_info']) {
                    if ($key === "User") {
                        $user_id = validate_non_negative_integer($value, "User", $lineNumber);
                        $current_service['Users'][$user_id] = ['ExtraFields' => "", 'Bio' => "", 'Signature' => ""];
                        if ($verbose) echo "Line {$lineNumber}: User ID set to {$user_id}\n";
                    } elseif ($user_id !== null) {
                        if ($key === "Name") $current_service['Users'][$user_id]['Name'] = $value;
                        elseif ($key === "Handle") $current_service['Users'][$user_id]['Handle'] = $value;
                        elseif ($key === "Email") $current_service['Users'][$user_id]['Email'] = $value;
                        elseif ($key === "Phone") $current_service['Users'][$user_id]['Phone'] = $value;
                        elseif ($key === "Location") $current_service['Users'][$user_id]['Location'] = $value;
                        elseif ($key === "Website") $current_service['Users'][$user_id]['Website'] = $value;
                        elseif ($key === "Avatar") $current_service['Users'][$user_id]['Avatar'] = $value;
                        elseif ($key === "Banner") $current_service['Users'][$user_id]['Banner'] = $value;
                        elseif ($key === "Joined") $current_service['Users'][$user_id]['Joined'] = $value;
                        elseif ($key === "Birthday") $current_service['Users'][$user_id]['Birthday'] = $value;
                        elseif ($key === "HashTags") $current_service['Users'][$user_id]['HashTags'] = $value;
                        if ($verbose && in_array($key, ["Name", "Handle", "Email", "Phone", "Location", "Website", "Avatar", "Banner", "Joined", "Birthday", "HashTags"])) {
                            echo "Line {$lineNumber}: {$key} set to {$value}\n";
                        }
                    }
                    if ($key === "PinnedMessage") {
                        $current_service['PinnedMessage'] = validate_non_negative_integer($value, "PinnedMessage", $lineNumber);
                        if ($verbose) echo "Line {$lineNumber}: Pinned Message set to {$value}\n";
                    } elseif ($line === "--- Start ExtraFields Body ---") {
                        if ($user_id !== null) {
                            $current_extrafields = [];
                            $in_section['extrafields_body'] = true;
                            if ($verbose) echo "Line {$lineNumber}: Starting extrafields body\n";
                        }
                    } elseif ($line === "--- End ExtraFields Body ---") {
                        if ($user_id !== null && isset($current_extrafields)) {
                            $current_service['Users'][$user_id]['ExtraFields'] = implode("\n", $current_extrafields);
                            unset($current_extrafields);
                            $in_section['extrafields_body'] = false;
                            if ($verbose) echo "Line {$lineNumber}: Ending extrafields body\n";
                        }
                    } elseif ($in_section['extrafields_body'] && isset($current_extrafields)) {
                        $current_extrafields[] = $line;
                        if ($verbose) echo "Line {$lineNumber}: Adding to extrafields body: {$line}\n";
                    } elseif ($line === "--- Start Bio Body ---") {
                        if ($user_id !== null) {
                            $current_bio = [];
                            $in_section['bio_body'] = true;
                            if ($verbose) echo "Line {$lineNumber}: Starting bio body\n";
                        }
                    } elseif ($line === "--- End Bio Body ---") {
                        if ($user_id !== null && $current_bio !== null) {
                            $current_service['Users'][$user_id]['Bio'] = implode("\n", $current_bio);
                            $current_bio = null;
                            $in_section['bio_body'] = false;
                            if ($verbose) echo "Line {$lineNumber}: Ending bio body\n";
                        }
                    } elseif ($in_section['bio_body'] && $current_bio !== null) {
                        $current_bio[] = $line;
                        if ($verbose) echo "Line {$lineNumber}: Adding to bio body: {$line}\n";
                    } elseif ($line === "--- Start Signature Body ---") {
                        if ($user_id !== null) {
                            $current_signature = [];
                            $in_section['signature_body'] = true;
                            if ($verbose) echo "Line {$lineNumber}: Starting signature body\n";
                        }
                    } elseif ($line === "--- End Signature Body ---") {
                        if ($user_id !== null && isset($current_signature)) {
                            $current_service['Users'][$user_id]['Signature'] = implode("\n", $current_signature);
                            unset($current_signature);
                            $in_section['signature_body'] = false;
                            if ($verbose) echo "Line {$lineNumber}: Ending signature body\n";
                        }
                    } elseif ($in_section['signature_body'] && isset($current_signature)) {
                        $current_signature[] = $line;
                        if ($verbose) echo "Line {$lineNumber}: Adding to signature body: {$line}\n";
                    }
                } elseif ($in_section['message_list'] && $in_section['message_thread']) {
                    if ($key === "Thread") $current_thread['Thread'] = validate_non_negative_integer($value, "Thread", $lineNumber);
                    elseif ($key === "Category") $current_thread['Category'] = array_map('trim', explode(",", $value));
                    elseif ($key === "Forum") $current_thread['Forum'] = array_map('trim', explode(",", $value));
                    elseif ($key === "Title") $current_thread['Title'] = $value;
                    elseif ($key === "Type") $current_thread['Type'] = $value;
                    elseif ($key === "State") $current_thread['State'] = $value;
                    elseif ($key === "Keywords") $current_thread['Keywords'] = $value;
                    elseif ($key === "Author") $current_message['Author'] = $value;
                    elseif ($key === "AuthorID") $current_message['AuthorID'] = validate_non_negative_integer($value, "AuthorID", $lineNumber);
                    elseif ($key === "Time") $current_message['Time'] = $value;
                    elseif ($key === "Date") $current_message['Date'] = $value;
                    elseif ($key === "EditTime") $current_message['EditTime'] = $value;
                    elseif ($key === "EditDate") $current_message['EditDate'] = $value;
                    elseif ($key === "EditAuthor") $current_message['EditAuthor'] = $value;
                    elseif ($key === "EditAuthorID") $current_message['EditAuthorID'] = validate_non_negative_integer($value, "EditAuthorID", $lineNumber);
                    elseif ($key === "SubType") $current_message['SubType'] = $value;
                    elseif ($key === "SubTitle") $current_message['SubTitle'] = $value;
                    elseif ($key === "Tags") $current_message['Tags'] = $value;
                    elseif ($key === "Post") {
                        $post_value = validate_non_negative_integer($value, "Post", $lineNumber);
                        $current_message['Post'] = $post_value;
                        if (!isset($current_thread['post_ids'])) {
                            $current_thread['post_ids'] = [];
                        }
                        if (in_array($post_value, $current_thread['post_ids'])) {
                            throw new \Exception(sprintf("Duplicate 'Post' value '%s' on line %d.", $post_value, $lineNumber));
                        }
                        $current_thread['post_ids'][] = $post_value;
                    }

                    if ($verbose && $key) {
                        if (is_array($value)) $value = implode(', ', $value);
                        echo "Line {$lineNumber}: {$key} set to {$value}\n";
                    }
                }
            }
        }
    } catch (\Exception $e) {
        // Re-throw the exception to mimic Python's behavior of not catching specific exceptions
        throw $e;
    }

    return $services;
}

/**
 * Serialize an array of services into the archive text format.
 *
 * @param array $services The array of service data to serialize.
 * @param string $line_ending The desired line ending ('lf', 'crlf', or 'cr').
 * @return string The serialized data as a single string.
 */
function services_to_string(array $services, string $line_ending = 'lf'): string
{
    $output = [];

    foreach ($services as $service) {
        // Service wrapper
        $output[] = '--- Start Archive Service ---';
        $output[] = 'Entry: ' . ($service['Entry'] ?? '');
        $output[] = 'Service: ' . ($service['Service'] ?? '');
        $output[] = 'ServiceType: ' . ($service['ServiceType'] ?? '');
        $output[] = 'ServiceLocation: ' . ($service['ServiceLocation'] ?? '');
        $output[] = 'TimeZone: ' . ($service['TimeZone'] ?? 'UTC');

        // Info section
        if (!empty($service['Info'])) {
            $output[] = 'Info:';
            $output[] = '--- Start Info Body ---';
            // Split the multi-line string into an array of lines
            foreach (preg_split('/\R/', $service['Info']) as $line) {
                $output[] = $line;
            }
            $output[] = '--- End Info Body ---';
            $output[] = '';
        }

        // User list
        $users = $service['Users'] ?? [];
        if (!empty($users)) {
            $output[] = '--- Start User List ---';
            foreach ($users as $uid => $user) {
                $output[] = '--- Start User Info ---';
                $output[] = 'User: ' . $uid;
                $output[] = 'Name: ' . ($user['Name'] ?? '');
                $output[] = 'Handle: ' . ($user['Handle'] ?? '');
                $output[] = 'Email: ' . ($user['Email'] ?? '');
                $output[] = 'Phone: ' . ($user['Phone'] ?? '');
                $output[] = 'Location: ' . ($user['Location'] ?? '');
                $output[] = 'Website: ' . ($user['Website'] ?? '');
                $output[] = 'Avatar: ' . ($user['Avatar'] ?? '');
                $output[] = 'Banner: ' . ($user['Banner'] ?? '');
                $output[] = 'Joined: ' . ($user['Joined'] ?? '');
                $output[] = 'Birthday: ' . ($user['Birthday'] ?? '');
                $output[] = 'HashTags: ' . ($user['HashTags'] ?? '');
                $output[] = 'PinnedMessage: ' . ($user['PinnedMessage'] ?? '0');
                
                // ExtraFields body
                $output[] = 'ExtraFields:';
                $output[] = '--- Start ExtraFields Body ---';
                foreach (preg_split('/\R/', $user['ExtraFields'] ?? '') as $line) {
                    $output[] = $line;
                }
                $output[] = '--- End ExtraFields Body ---';
                
                // Bio body
                $output[] = 'Bio:';
                $output[] = '--- Start Bio Body ---';
                foreach (preg_split('/\R/', $user['Bio'] ?? '') as $line) {
                    $output[] = $line;
                }
                $output[] = '--- End Bio Body ---';

                // Signature body
                $output[] = 'Signature:';
                $output[] = '--- Start Signature Body ---';
                foreach (preg_split('/\R/', $user['Signature'] ?? '') as $line) {
                    $output[] = $line;
                }
                $output[] = '--- End Signature Body ---';
                $output[] = '--- End User Info ---';
                $output[] = '';
            }
            $output[] = '--- End User List ---';
            $output[] = '';
        }

        // Categorization list
        $categorization = $service['Categorization'] ?? [];
        if (!empty($categorization)) {
            $output[] = '--- Start Categorization List ---';
            $output[] = 'Categories: ' . implode(', ', $categorization['Categories'] ?? []);
            $output[] = 'Forums: ' . implode(', ', $categorization['Forums'] ?? []);
            $output[] = '--- End Categorization List ---';
            $output[] = '';
        }

        // Detailed categories
        foreach ($service['Categories'] ?? [] as $cat) {
            $output[] = '--- Start Category List ---';
            $output[] = 'Kind: ' . ($cat['Type'] ?? '') . ', ' . ($cat['Level'] ?? '');
            $output[] = 'ID: ' . ($cat['ID'] ?? '0');
            $output[] = 'InSub: ' . ($cat['InSub'] ?? '0');
            $output[] = 'Headline: ' . ($cat['Headline'] ?? '');
            $output[] = 'Description:';
            $output[] = '--- Start Description Body ---';
            foreach (preg_split('/\R/', $cat['Description'] ?? '') as $line) {
                $output[] = $line;
            }
            $output[] = '--- End Description Body ---';
            $output[] = '--- End Category List ---';
            $output[] = '';
        }

        // Message list
        $threads = $service['MessageThreads'] ?? [];
        if (!empty($threads)) {
            $output[] = '--- Start Message List ---';
            if (!empty($service['Interactions'])) {
                $output[] = 'Interactions: ' . implode(', ', $service['Interactions']);
            }
            if (!empty($service['Status'])) {
                $output[] = 'Status: ' . implode(', ', $service['Status']);
            }
            $output[] = '';

            foreach ($threads as $thread) {
                $output[] = '--- Start Message Thread ---';
                $output[] = 'Thread: ' . ($thread['Thread'] ?? '0');
                $output[] = 'Title: ' . ($thread['Title'] ?? '');
                $output[] = 'Type: ' . ($thread['Type'] ?? '');
                $output[] = 'State: ' . ($thread['State'] ?? '');
                $output[] = 'Keywords: ' . ($thread['Keywords'] ?? '');
                $output[] = 'Category: ' . implode(', ', $thread['Category'] ?? []);
                $output[] = 'Forum: ' . implode(', ', $thread['Forum'] ?? []);
                $output[] = '';

                foreach ($thread['Messages'] ?? [] as $msg) {
                    $output[] = '--- Start Message Post ---';
                    $output[] = 'Author: ' . ($msg['Author'] ?? '');
                    $output[] = 'AuthorID: ' . ($msg['AuthorID'] ?? '0');
                    $output[] = 'Time: ' . ($msg['Time'] ?? '');
                    $output[] = 'Date: ' . ($msg['Date'] ?? '');
                    $output[] = 'EditTime: ' . ($msg['EditTime'] ?? '');
                    $output[] = 'EditDate: ' . ($msg['EditDate'] ?? '');
                    $output[] = 'EditAuthor: ' . ($msg['EditAuthor'] ?? '');
                    $output[] = 'EditAuthorID: ' . ($msg['EditAuthorID'] ?? '0');
                    $output[] = 'SubType: ' . ($msg['SubType'] ?? '');
                    $output[] = 'SubTitle: ' . ($msg['SubTitle'] ?? '');
                    $output[] = 'Tags: ' . ($msg['Tags'] ?? '');
                    $output[] = 'Post: ' . ($msg['Post'] ?? '0');
                    $output[] = 'PinnedID: ' . ($msg['PinnedID'] ?? '0');
                    $output[] = 'Nested: ' . ($msg['Nested'] ?? '0');

                    // Message body
                    $output[] = 'Message:';
                    $output[] = '--- Start Message Body ---';
                    foreach (preg_split('/\R/', $msg['Message'] ?? '') as $line) {
                        $output[] = $line;
                    }
                    $output[] = '--- End Message Body ---';

                    // Polls
                    if (!empty($msg['Polls'])) {
                        $output[] = 'Polls:';
                        $output[] = '--- Start Poll List ---';
                        foreach ($msg['Polls'] as $poll) {
                            $output[] = '--- Start Poll Body ---';
                            $output[] = 'Num: ' . ($poll['Num'] ?? '0');
                            $output[] = 'Question: ' . ($poll['Question'] ?? '');
                            $output[] = 'Answers: ' . implode(', ', $poll['Answers'] ?? []);
                            
                            $results = array_map('strval', $poll['Results'] ?? []);
                            $output[] = 'Results: ' . implode(', ', $results);

                            $percentages = array_map(function($p) {
                                return sprintf('%.1f', (float)$p);
                            }, $poll['Percentage'] ?? []);
                            $output[] = 'Percentage: ' . implode(', ', $percentages);

                            $output[] = 'Votes: ' . ($poll['Votes'] ?? '0');
                            $output[] = '--- End Poll Body ---';
                        }
                        $output[] = '--- End Poll List ---';
                    }
                    $output[] = '--- End Message Post ---';
                    $output[] = '';
                }

                $output[] = '--- End Message Thread ---';
                $output[] = '';
            }
            $output[] = '--- End Message List ---';
            $output[] = '';
        }

        // Close service
        $output[] = '--- End Archive Service ---';
        $output[] = '';
    }

    // Join all lines with LF, then replace with the desired line ending
    $data = implode("\n", $output);
    if (strtolower($line_ending) === 'crlf') {
        $data = str_replace("\n", "\r\n", $data);
    } elseif (strtolower($line_ending) === 'cr') {
        $data = str_replace("\n", "\r", $data);
    }

    return $data;
}

/**
 * Displays a formatted summary of service data to the console.
 *
 * @param array $services The array of service data to display.
 * @return void
 */
function display_services(array $services): void
{
    foreach ($services as $service) {
        echo "Service Entry: " . ($service['Entry'] ?? '') . "\n";
        echo "Service: " . ($service['Service'] ?? '') . "\n";
        echo "Service Type: " . ($service['ServiceType'] ?? '') . "\n";
        echo "Service Location: " . ($service['ServiceLocation'] ?? '') . "\n";
        echo "TimeZone: " . ($service['TimeZone'] ?? '') . "\n";

        if (!empty($service['Info'])) {
            echo "Info: " . trim($service['Info']) . "\n";
        }

        echo "Interactions: " . implode(', ', $service['Interactions'] ?? []) . "\n";
        echo "Status: " . implode(', ', $service['Status'] ?? []) . "\n";

        if (!empty($service['Categorization'])) {
            foreach ($service['Categorization'] as $category_type => $category_levels) {
                // Note: The original Python code had a bug here, printing the type twice.
                // This is the corrected version.
                echo "{$category_type}: " . implode(', ', $category_levels) . "\n";
            }
        }
        echo "\n";

        echo "Category List:\n";
        foreach ($service['Categories'] ?? [] as $category) {
            echo "  Type: " . ($category['Type'] ?? '') . ", Level: " . ($category['Level'] ?? '') . "\n";
            echo "  ID: " . ($category['ID'] ?? '') . "\n";
            echo "  In SubID: " . ($category['InSub'] ?? '') . "\n";
            echo "  Headline: " . ($category['Headline'] ?? '') . "\n";
            echo "  Description: " . trim($category['Description'] ?? '') . "\n";
            echo "\n";
        }

        echo "User List:\n";
        foreach ($service['Users'] ?? [] as $user_id => $user_info) {
            echo "  User ID: {$user_id}\n";
            echo "    Name: " . ($user_info['Name'] ?? '') . "\n";
            echo "    Handle: " . ($user_info['Handle'] ?? '') . "\n";
            echo "    Email: " . ($user_info['Email'] ?? '') . "\n";
            echo "    Phone: " . ($user_info['Phone'] ?? '') . "\n";
            echo "    Location: " . ($user_info['Location'] ?? '') . "\n";
            echo "    Website: " . ($user_info['Website'] ?? '') . "\n";
            echo "    Avatar: " . ($user_info['Avatar'] ?? '') . "\n";
            echo "    Banner: " . ($user_info['Banner'] ?? '') . "\n";
            echo "    Joined: " . ($user_info['Joined'] ?? '') . "\n";
            echo "    Birthday: " . ($user_info['Birthday'] ?? '') . "\n";
            echo "    HashTags: " . ($user_info['HashTags'] ?? '') . "\n";
            echo "    ExtraFields:\n";
            echo "      " . trim($user_info['ExtraFields'] ?? '') . "\n";
            echo "    Bio:\n";
            echo "      " . trim($user_info['Bio'] ?? '') . "\n";
            echo "    Signature:\n";
            echo "      " . trim($user_info['Signature'] ?? '') . "\n";
            echo "\n";
        }

        echo "Message Threads:\n";
        foreach ($service['MessageThreads'] ?? [] as $idx => $thread) {
            echo "  --- Message Thread " . ($idx + 1) . " ---\n";
            if (!empty($thread['Title'])) {
                echo "    Title: " . $thread['Title'] . "\n";
            }
            if (!empty($thread['Category'])) {
                echo "    Category: " . implode(', ', $thread['Category']) . "\n";
            }
            if (!empty($thread['Forum'])) {
                echo "    Forum: " . implode(', ', $thread['Forum']) . "\n";
            }
            if (!empty($thread['Type'])) {
                echo "    Type: " . $thread['Type'] . "\n";
            }
            if (!empty($thread['State'])) {
                echo "    State: " . $thread['State'] . "\n";
            }
            if (!empty($thread['Keywords'])) {
                echo "    Keywords: " . $thread['Keywords'] . "\n";
            }

            foreach ($thread['Messages'] ?? [] as $message) {
                $defaultSubType = (($message['Post'] ?? 0) == 1 || ($message['Nested'] ?? 1) == 0) ? 'Post' : 'Reply';
                $subType = $message['SubType'] ?? $defaultSubType;

                echo sprintf("    %s (%s on %s): [%s] Post ID: %s Nested: %s\n",
                    $message['Author'] ?? '',
                    $message['Time'] ?? '',
                    $message['Date'] ?? '',
                    $subType,
                    $message['Post'] ?? '',
                    $message['Nested'] ?? ''
                );

                echo "      " . trim($message['Message'] ?? '') . "\n";

                if (!empty($message['Polls'])) {
                    echo "      Polls:\n";
                    foreach ($message['Polls'] as $poll) {
                        echo "        Poll " . ($poll['Num'] ?? '') . ":\n";
                        echo "          Question: " . ($poll['Question'] ?? '') . "\n";
                        echo "          Answers: " . implode(", ", $poll['Answers'] ?? []) . "\n";
                        
                        $results = array_map('strval', $poll['Results'] ?? []);
                        echo "          Results: " . implode(", ", $results) . "\n";

                        $percentages = array_map(function($p) {
                            return sprintf('%.2f', (float)$p);
                        }, $poll['Percentage'] ?? []);
                        echo "          Percentage: " . implode(", ", $percentages) . "\n";
                        
                        echo "          Votes: " . ($poll['Votes'] ?? '') . "\n";
                    }
                }
            }
            echo "\n";
        }
    }
}

/**
 * Render the services list as a styled HTML document string.
 *
 * @param array $services An array of associative arrays representing services.
 * @return string A complete HTML page as a string.
 */
function services_to_html(array $services): string
{
    $lines = [];

    // --- Document Head ---
    $lines[] = '<!DOCTYPE html>';
    $lines[] = '<html lang="en">';
    $lines[] = '<head>';
    $lines[] = '    <meta charset="UTF-8">';
    $lines[] = '    <meta name="viewport" content="width=device-width, initial-scale=1.0">';
    $lines[] = '    <title>Services Report</title>';
    $lines[] = '    <style>';
    $lines[] = '        body { font-family: Arial, sans-serif; margin: 20px; background: #f9f9f9; }';
    $lines[] = '        .service-card { background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 16px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }';
    $lines[] = '        .service-card h2 { margin-top: 0; color: #333; }';
    $lines[] = '        .thread-card { background: #fafafa; border-left: 4px solid #007BFF; padding: 12px; margin: 10px 0; }';
    $lines[] = '        .message-list { list-style: none; padding-left: 0; }';
    $lines[] = '        .message-list li { margin-bottom: 10px; }';
    $lines[] = '        .poll-card { background: #f0f8ff; border: 1px solid #cce; border-radius: 4px; padding: 10px; margin: 10px 0; }';
    $lines[] = '    </style>';
    $lines[] = '</head>';
    $lines[] = '<body>';
    $lines[] = '<div class="services-container">';

    // --- Service Cards ---
    foreach ($services as $svc) {
        $entry = htmlspecialchars($svc['Entry'] ?? '', ENT_QUOTES, 'UTF-8');
        $name = htmlspecialchars($svc['Service'] ?? '', ENT_QUOTES, 'UTF-8');
        $lines[] = '<div class="service-card">';
        $lines[] = sprintf('    <h2>Service Entry: %s — %s</h2>', $entry, $name);

        // Info
        $info = trim($svc['Info'] ?? '');
        if (!empty($info)) {
            $lines[] = sprintf(
                '    <p><strong>Info:</strong> <blockquote style="white-space: pre-wrap;">%s</blockquote></p>',
                htmlspecialchars($info, ENT_QUOTES, 'UTF-8')
            );
        }

        // Interactions & Status
        $interactions = $svc['Interactions'] ?? [];
        if (!empty($interactions)) {
            $items = implode(', ', array_map('htmlspecialchars', $interactions));
            $lines[] = sprintf('    <p><strong>Interactions:</strong> %s</p>', $items);
        }
        $status = $svc['Status'] ?? [];
        if (!empty($status)) {
            $items = implode(', ', array_map('htmlspecialchars', $status));
            $lines[] = sprintf('    <p><strong>Status:</strong> %s</p>', $items);
        }

        // Categories
        $cats = $svc['Categories'] ?? [];
        if (!empty($cats)) {
            $lines[] = '    <h3>Categories</h3>';
            $lines[] = '    <ul>';
            foreach ($cats as $cat) {
                $headline = htmlspecialchars($cat['Headline'] ?? '', ENT_QUOTES, 'UTF-8');
                $level = htmlspecialchars($cat['Level'] ?? '', ENT_QUOTES, 'UTF-8');
                $lines[] = sprintf('        <li>%s (<em>%s</em>)</li>', $headline, $level);
            }
            $lines[] = '    </ul>';
        }
        
        // Users
        $users = $svc['Users'] ?? [];
        if (!empty($users)) {
            $lines[] = '    <h3>Users</h3>';
            $lines[] = '    <ul>';
            foreach ($users as $uid => $u) {
                $safe_uid = htmlspecialchars($uid, ENT_QUOTES, 'UTF-8');
                $uname = htmlspecialchars($u['Name'] ?? '', ENT_QUOTES, 'UTF-8');
                $handle = htmlspecialchars($u['Handle'] ?? '', ENT_QUOTES, 'UTF-8');
                $bio = trim($u['Bio'] ?? '');
                
                $lines[] = sprintf('        <li><strong>%s</strong>: %s (%s)</li>', $safe_uid, $uname, $handle);
                if (!empty($bio)) {
                    $lines[] = sprintf(
                        '            <blockquote style="white-space: pre-wrap;">%s</blockquote>',
                        htmlspecialchars($bio, ENT_QUOTES, 'UTF-8')
                    );
                }
            }
            $lines[] = '    </ul>';
        }

        // Message Threads
        $threads = $svc['MessageThreads'] ?? [];
        if (!empty($threads)) {
            $lines[] = '    <h3>Message Threads</h3>';
            foreach ($threads as $th) {
                $title = htmlspecialchars($th['Title'] ?? '', ENT_QUOTES, 'UTF-8');
                $lines[] = '    <div class="thread-card">';
                $lines[] = sprintf('        <h4>%s</h4>', $title);

                $msgs = $th['Messages'] ?? [];
                if (!empty($msgs)) {
                    $lines[] = '        <ul class="message-list">';
                    foreach ($msgs as $msg) {
                        $author = htmlspecialchars($msg['Author'] ?? '', ENT_QUOTES, 'UTF-8');
                        $body = trim($msg['Message'] ?? '');
                        $lines[] = sprintf(
                            '            <li><strong>%s</strong>: <blockquote style="white-space: pre-wrap;">%s</blockquote></li>',
                            $author,
                            htmlspecialchars($body, ENT_QUOTES, 'UTF-8')
                        );
                    }
                    $lines[] = '        </ul>';
                }
                $lines[] = '    </div>';
            }
        }

        $lines[] = '</div>'; // Closes .service-card
    }

    $lines[] = '</div>'; // Closes .services-container
    $lines[] = '</body>';
    $lines[] = '</html>';

    return implode("\n", $lines);
}

/**
 * Parses a file (compressed or not) and returns the services data structure.
 * Assumes parse_lines() is defined elsewhere.
 */
function parse_file(string $filename, bool $validate_only = false, bool $verbose = false): array
{
    $handle = open_compressed_file($filename);
    if ($handle === false) {
        throw new \Exception("Could not open file: {$filename}");
    }

    $lines = [];
    while (($line = fgets($handle)) !== false) {
        $lines[] = rtrim($line, "\r\n");
    }
    fclose($handle);

    return parse_lines($lines, $validate_only, $verbose);
}

/**
 * Parses a string and returns the services data structure.
 * Assumes parse_lines() is defined elsewhere.
 */
function parse_string(string $data, bool $validate_only = false, bool $verbose = false): array
{
    $lines = explode("\n", $data);
    return parse_lines($lines, $validate_only, $verbose);
}

/**
 * Parses a file and displays the services.
 * Assumes display_services() is defined elsewhere.
 */
function display_services_from_file(string $filename): void
{
    $services = parse_file($filename, false, false);
    display_services($services);
}

/**
 * Parses a file and returns the services as an HTML string.
 */
function services_to_html_from_file(string $filename): string
{
    $services = parse_file($filename, false, false);
    return services_to_html($services);
}

/**
 * Saves a services data structure to an HTML file (compressed or not).
 */
function save_services_to_html_file(array $services, string $filename): void
{
    $html_content = services_to_html($services);
    save_compressed_file($html_content, $filename);
}

/**
 * A wrapper to parse a file and save the result directly to an HTML file.
 */
function save_services_to_html_file_from_file(string $filename, string $outfilename): void
{
    $services = parse_file($filename, false, false);
    save_services_to_html_file($services, $outfilename);
}

/**
 * Convert the services data structure to a JSON string.
 */
function to_json(array $services): string
{
    // JSON_PRETTY_PRINT = indent=2
    // JSON_UNESCAPED_UNICODE = ensure_ascii=False
    return json_encode($services, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
}

/**
 * Convert a JSON string back to the services data structure.
 */
function from_json(string $json_str): array
{
    return json_decode($json_str, true); // true converts objects to associative arrays
}

/**
 * Load the services data structure from a JSON file (compressed or not).
 */
function load_from_json_file(string $json_filename): array
{
    $handle = open_compressed_file($json_filename);
    if ($handle === false) {
        throw new \Exception("Could not open JSON file: {$json_filename}");
    }
    $json_data = stream_get_contents($handle);
    fclose($handle);
    return from_json($json_data);
}

/**
 * Save the services data structure to a JSON file (compressed or not).
 */
function save_to_json_file(array $services, string $json_filename): void
{
    $json_data = to_json($services);
    save_compressed_file($json_data, $json_filename);
}

<?php

/**
 * Initialize an empty service structure.
 */
function init_empty_service(int $entry, string $service_name, string $service_type, string $service_location, string $time_zone = "UTC", string $info = ''): array
{
    return [
        'Entry' => $entry,
        'Service' => $service_name,
        'ServiceType' => $service_type,
        'ServiceLocation' => $service_location,
        'TimeZone' => $time_zone,
        'Info' => $info,
        'Users' => [],
        'MessageThreads' => [],
        'Categories' => [],
        'Interactions' => [],
        'Categorization' => [],
    ];
}

/**
 * Add a user to the service.
 * Note: Corrected a bug from the original Python where 'Avatar' and 'Banner' were assigned the wrong variable.
 */
function add_user(array &$service, int $user_id, string $name, string $handle, string $emailaddr, string $phonenum, string $location, string $website, string $avatar, string $banner, string $joined, string $birthday, string $hashtags, int $pinnedmessage, string $extrafields, string $bio, string $signature): void
{
    $service['Users'][$user_id] = [
        'Name' => $name,
        'Handle' => $handle,
        'Email' => $emailaddr,
        'Phone' => $phonenum,
        'Location' => $location,
        'Website' => $website,
        'Avatar' => $avatar,
        'Banner' => $banner,
        'Joined' => $joined,
        'Birthday' => $birthday,
        'HashTags' => $hashtags,
        'PinnedMessage' => $pinnedmessage,
        'ExtraFields' => $extrafields,
        'Bio' => $bio,
        'Signature' => $signature,
    ];
}

/**
 * Add a category to the service.
 */
function add_category(array &$service, string $kind, string $category_type, string $category_level, int $category_id, int $insub, string $headline, string $description): void
{
    $service['Categories'][] = [
        'Kind' => "{$kind}, {$category_level}",
        'Type' => $category_type,
        'Level' => $category_level,
        'ID' => $category_id,
        'InSub' => $insub,
        'Headline' => $headline,
        'Description' => $description,
    ];

    if (!isset($service['Categorization'][$category_type])) {
        $service['Categorization'][$category_type] = [];
    }
    if (!in_array($category_level, $service['Categorization'][$category_type])) {
        $service['Categorization'][$category_type][] = $category_level;
    }

    if ($insub !== 0) {
        $id_exists = false;
        foreach ($service['Categories'] as $cat) {
            if ($cat['ID'] === $insub) {
                $id_exists = true;
                break;
            }
        }
        if (!$id_exists) {
            throw new InvalidArgumentException("InSub value '{$insub}' does not match any existing ID in service.");
        }
    }
}

/**
 * Add a message thread to the service.
 */
function add_message_thread(array &$service, int $thread_id, string $title, string $category, string $forum, string $thread_type, string $thread_state, string $thread_keywords): void
{
    $service['MessageThreads'][] = [
        'Thread' => $thread_id,
        'Title' => $title,
        'Category' => !empty($category) ? explode(',', $category) : [],
        'Forum' => !empty($forum) ? explode(',', $forum) : [],
        'Type' => $thread_type,
        'State' => $thread_state,
        'Keywords' => $thread_keywords,
        'Messages' => [],
    ];
}

/**
 * Add a message post to a specific thread.
 * Note: The original Python code had an undefined 'subtitle' variable, which has been omitted.
 */
function add_message_post(array &$service, int $thread_id, string $author, int $authorid, string $time, string $date, string $edittime, string $editdate, string $editauthor, int $editauthorid, string $subtype, string $tags, int $post_id, int $pinned_id, int $nested, string $message): void
{
    foreach ($service['MessageThreads'] as &$thread) {
        if ($thread['Thread'] === $thread_id) {
            $thread['Messages'][] = [
                'Author' => $author,
                'AuthorID' => $authorid,
                'Time' => $time,
                'Date' => $date,
                'EditTime' => $edittime,
                'EditDate' => $editdate,
                'EditAuthor' => $editauthor,
                'EditAuthorID' => $editauthorid,
                'SubType' => $subtype,
                'Tags' => $tags,
                'Post' => $post_id,
                'PinnedID' => $pinned_id,
                'Nested' => $nested,
                'Message' => $message,
            ];
            return; // Exit after adding the post
        }
    }
    throw new InvalidArgumentException("Thread ID {$thread_id} not found in service.");
}

/**
 * Add a poll to a specific message post.
 */
function add_poll(array &$service, int $thread_id, int $post_id, int $poll_num, string $question, array $answers, array $results, array $percentages, int $votes): void
{
    foreach ($service['MessageThreads'] as &$thread) {
        if ($thread['Thread'] === $thread_id) {
            foreach ($thread['Messages'] as &$message) {
                if ($message['Post'] === $post_id) {
                    if (!isset($message['Polls'])) {
                        $message['Polls'] = [];
                    }
                    $message['Polls'][] = [
                        'Num' => $poll_num,
                        'Question' => $question,
                        'Answers' => $answers,
                        'Results' => $results,
                        'Percentage' => $percentages,
                        'Votes' => $votes,
                    ];
                    return; // Exit after adding the poll
                }
            }
            throw new InvalidArgumentException("Post ID {$post_id} not found in thread {$thread_id}.");
        }
    }
    throw new InvalidArgumentException("Thread ID {$thread_id} not found in service.");
}

/**
 * Add a new service to the list of services.
 */
function add_service(array &$services, int $entry, string $service_name, string $service_type, string $service_location, string $time_zone = "UTC", ?string $info = null): array
{
    $new_service = [
        'Entry' => $entry,
        'Service' => $service_name,
        'ServiceType' => $service_type,
        'ServiceLocation' => $service_location,
        'TimeZone' => $time_zone,
        'Info' => $info ?? '',
        'Interactions' => [],
        'Status' => [],
        'Categorization' => ['Categories' => [], 'Forums' => []],
        'Categories' => [],
        'Users' => [],
        'MessageThreads' => [],
    ];
    $services[] = $new_service;
    return $new_service; // Return the newly created service
}

/**
 * Remove a user from the service.
 */
function remove_user(array &$service, int $user_id): void
{
    if (isset($service['Users'][$user_id])) {
        unset($service['Users'][$user_id]);
    } else {
        throw new InvalidArgumentException("User ID {$user_id} not found in service.");
    }
}

/**
 * Remove a category from the service.
 */
function remove_category(array &$service, int $category_id): void
{
    $key_to_remove = null;
    foreach ($service['Categories'] as $key => $category) {
        if ($category['ID'] === $category_id) {
            $key_to_remove = $key;
            break;
        }
    }

    if ($key_to_remove !== null) {
        unset($service['Categories'][$key_to_remove]);
        // Optional: Re-index the array to prevent gaps
        $service['Categories'] = array_values($service['Categories']);
    } else {
        throw new InvalidArgumentException("Category ID {$category_id} not found in service.");
    }
}

/**
 * Remove a message thread from the service.
 */
function remove_message_thread(array &$service, int $thread_id): void
{
    $key_to_remove = null;
    foreach ($service['MessageThreads'] as $key => $thread) {
        if ($thread['Thread'] === $thread_id) {
            $key_to_remove = $key;
            break;
        }
    }

    if ($key_to_remove !== null) {
        unset($service['MessageThreads'][$key_to_remove]);
        $service['MessageThreads'] = array_values($service['MessageThreads']);
    } else {
        throw new InvalidArgumentException("Thread ID {$thread_id} not found in service.");
    }
}

/**
 * Remove a message post from a specific thread.
 */
function remove_message_post(array &$service, int $thread_id, int $post_id): void
{
    foreach ($service['MessageThreads'] as &$thread) {
        if ($thread['Thread'] === $thread_id) {
            $key_to_remove = null;
            foreach ($thread['Messages'] as $key => $message) {
                if ($message['Post'] === $post_id) {
                    $key_to_remove = $key;
                    break;
                }
            }

            if ($key_to_remove !== null) {
                unset($thread['Messages'][$key_to_remove]);
                $thread['Messages'] = array_values($thread['Messages']);
                return; // Exit after removing
            } else {
                throw new InvalidArgumentException("Post ID {$post_id} not found in thread {$thread_id}.");
            }
        }
    }
    throw new InvalidArgumentException("Thread ID {$thread_id} not found in service.");
}


/**
 * Remove a service from the list of services.
 */
function remove_service(array &$services, int $entry): void
{
    $key_to_remove = null;
    foreach ($services as $key => $service) {
        if ($service['Entry'] === $entry) {
            $key_to_remove = $key;
            break;
        }
    }

    if ($key_to_remove !== null) {
        unset($services[$key_to_remove]);
        $services = array_values($services);
    } else {
        throw new InvalidArgumentException("Service entry {$entry} not found.");
    }
}

?>