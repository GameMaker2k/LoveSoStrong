#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals, generators, with_statement, nested_scopes
import re
import sys
import json
from collections import OrderedDict
import io
import gzip
import bz2
import lzma
import marshal
import pickle
import ast
import binascii

# StringIO and BytesIO
try:
    from io import StringIO, BytesIO
except ImportError:
    try:
        from cStringIO import StringIO
        from cStringIO import StringIO as BytesIO
    except ImportError:
        from StringIO import StringIO
        from StringIO import StringIO as BytesIO

# Cross-version HTML escape
try:
    # Python 3
    from html import escape
except ImportError:
    # Python 2 fallback
    from xml.sax.saxutils import escape

PY2 = sys.version_info[0] == 2

# Compatibility for different string types between Python 2 and 3
try:
    unicode_type = unicode
    str_type = basestring
except NameError:
    unicode_type = str
    str_type = str

__program_name__ = "PyTextArchive";
__project__ = __program_name__;
__project_url__ = "https://github.com/GameMaker2k/PyTextArchive";
__version_info__ = (0, 4, 8, "RC 1", 1);
__version_date_info__ = (2025, 7, 26, "RC 1", 1);
__version_date__ = str(__version_date_info__[0]) + "." + str(__version_date_info__[1]).zfill(2) + "." + str(__version_date_info__[2]).zfill(2);
__revision__ = __version_info__[3];
__revision_id__ = "$Id$";
if(__version_info__[4] is not None):
 __version_date_plusrc__ = __version_date__ + "-" + str(__version_date_info__[4]);
if(__version_info__[4] is None):
 __version_date_plusrc__ = __version_date__;
if(__version_info__[3] is not None):
 __version__ = str(__version_info__[0]) + "." + str(__version_info__[1]) + "." + str(__version_info__[2]) + " " + str(__version_info__[3]);
if(__version_info__[3] is None):
 __version__ = str(__version_info__[0]) + "." + str(__version_info__[1]) + "." + str(__version_info__[2]);

compressionsupport = []
try:
    import gzip
    compressionsupport.append("gz")
    compressionsupport.append("gzip")
except ImportError:
    pass
try:
    import bz2
    compressionsupport.append("bz2")
    compressionsupport.append("bzip2")
except ImportError:
    pass
try:
    import lz4
    import lz4.frame
    compressionsupport.append("lz4")
except ImportError:
    pass
try:
    import lzo
    compressionsupport.append("lzo")
    compressionsupport.append("lzop")
except ImportError:
    pass
try:
    import zstandard
    compressionsupport.append("zst")
    compressionsupport.append("zstd")
    compressionsupport.append("zstandard")
except ImportError:
    try:
        import pyzstd.zstdfile
        compressionsupport.append("zst")
        compressionsupport.append("zstd")
        compressionsupport.append("zstandard")
    except ImportError:
        pass
try:
    import lzma
    compressionsupport.append("lzma")
    compressionsupport.append("xz")
except ImportError:
    try:
        from backports import lzma
        compressionsupport.append("lzma")
        compressionsupport.append("xz")
    except ImportError:
        pass
compressionsupport.append("zlib")
compressionsupport.append("zl")
compressionsupport.append("zz")
compressionsupport.append("Z")
compressionsupport.append("z")

compressionlist = ['auto']
compressionlistalt = []
outextlist = []
outextlistwd = []
if('gzip' in compressionsupport):
    compressionlist.append('gzip')
    compressionlistalt.append('gzip')
    outextlist.append('gz')
    outextlistwd.append('.gz')
if('bzip2' in compressionsupport):
    compressionlist.append('bzip2')
    compressionlistalt.append('bzip2')
    outextlist.append('bz2')
    outextlistwd.append('.bz2')
if('zstd' in compressionsupport):
    compressionlist.append('zstd')
    compressionlistalt.append('zstd')
    outextlist.append('zst')
    outextlistwd.append('.zst')
if('lz4' in compressionsupport):
    compressionlist.append('lz4')
    compressionlistalt.append('lz4')
    outextlist.append('lz4')
    outextlistwd.append('.lz4')
if('lzo' in compressionsupport):
    compressionlist.append('lzo')
    compressionlistalt.append('lzo')
    outextlist.append('lzo')
    outextlistwd.append('.lzo')
if('lzop' in compressionsupport):
    compressionlist.append('lzop')
    compressionlistalt.append('lzop')
    outextlist.append('lzop')
    outextlistwd.append('.lzop')
if('lzma' in compressionsupport):
    compressionlist.append('lzma')
    compressionlistalt.append('lzma')
    outextlist.append('lzma')
    outextlistwd.append('.lzma')
if('xz' in compressionsupport):
    compressionlist.append('xz')
    compressionlistalt.append('xz')
    outextlist.append('xz')
    outextlistwd.append('.xz')
if('zlib' in compressionsupport):
    compressionlist.append('zlib')
    compressionlistalt.append('zlib')
    outextlist.append('zz')
    outextlistwd.append('.zz')
    outextlist.append('zl')
    outextlistwd.append('.zl')
    outextlist.append('zlib')
    outextlistwd.append('.zlib')

def get_file_encoding(infile, closefp=True):
    if(hasattr(infile, "read") or hasattr(infile, "write")):
        fp = infile
    else:
        try:
            fp = open(infile, "rb")
        except FileNotFoundError:
            return False
    file_encoding = "UTF-8"
    fp.seek(0, 0)
    prefp = fp.read(2)
    if(prefp == binascii.unhexlify("fffe")):
        file_encoding = "UTF-16LE"
    elif(prefp == binascii.unhexlify("feff")):
        file_encoding = "UTF-16BE"
    fp.seek(0, 0)
    prefp = fp.read(3)
    if(prefp == binascii.unhexlify("efbbbf")):
        file_encoding = "UTF-8"
    elif(prefp == binascii.unhexlify("0efeff")):
        file_encoding = "SCSU"
    fp.seek(0, 0)
    prefp = fp.read(4)
    if(prefp == binascii.unhexlify("fffe0000")):
        file_encoding = "UTF-32LE"
    elif(prefp == binascii.unhexlify("0000feff")):
        file_encoding = "UTF-32BE"
    elif(prefp == binascii.unhexlify("dd736673")):
        file_encoding = "UTF-EBCDIC"
    elif(prefp == binascii.unhexlify("2b2f7638")):
        file_encoding = "UTF-7"
    elif(prefp == binascii.unhexlify("2b2f7639")):
        file_encoding = "UTF-7"
    elif(prefp == binascii.unhexlify("2b2f762b")):
        file_encoding = "UTF-7"
    elif(prefp == binascii.unhexlify("2b2f762f")):
        file_encoding = "UTF-7"
    fp.seek(0, 0)
    if(closefp):
        fp.close()
    return file_encoding

def get_file_encoding_from_string(instring, closefp=True):
    instringsfile = StringIO(instring)
    return get_file_encoding(instringsfile, closefp)

class ZlibFile:
    def __init__(self, file_path=None, fileobj=None, mode='rb', level=9, wbits=15, encoding=None, errors=None, newline=None):
        if file_path is None and fileobj is None:
            raise ValueError("Either file_path or fileobj must be provided")
        if file_path is not None and fileobj is not None:
            raise ValueError(
                "Only one of file_path or fileobj should be provided")

        self.file_path = file_path
        self.fileobj = fileobj
        self.mode = mode
        self.level = level
        self.wbits = wbits
        self.encoding = encoding
        self.errors = errors
        self.newline = newline
        self._compressed_data = b''
        self._decompressed_data = b''
        self._position = 0
        self._text_mode = 't' in mode

        # Force binary mode for internal handling
        internal_mode = mode.replace('t', 'b')

        if 'w' in mode or 'a' in mode or 'x' in mode:
            self.file = open(
                file_path, internal_mode) if file_path else fileobj
            self._compressor = zlib.compressobj(level, zlib.DEFLATED, wbits)
        elif 'r' in mode:
            if file_path:
                if os.path.exists(file_path):
                    self.file = open(file_path, internal_mode)
                    self._load_file()
                else:
                    raise FileNotFoundError(
                        "No such file: '{}'".format(file_path))
            elif fileobj:
                self.file = fileobj
                self._load_file()
        else:
            raise ValueError("Mode should be 'rb' or 'wb'")

    def _load_file(self):
        self.file.seek(0)
        self._compressed_data = self.file.read()
        if not self._compressed_data.startswith((b'\x78\x01', b'\x78\x5E', b'\x78\x9C', b'\x78\xDA')):
            raise ValueError("Invalid zlib file header")
        self._decompressed_data = zlib.decompress(
            self._compressed_data, self.wbits)
        if self._text_mode:
            self._decompressed_data = self._decompressed_data.decode(
                self.encoding or 'UTF-8', self.errors or 'strict')

    def write(self, data):
        if self._text_mode:
            data = data.encode(self.encoding or 'UTF-8',
                               self.errors or 'strict')
        compressed_data = self._compressor.compress(
            data) + self._compressor.flush(zlib.Z_SYNC_FLUSH)
        self.file.write(compressed_data)

    def read(self, size=-1):
        if size == -1:
            size = len(self._decompressed_data) - self._position
        data = self._decompressed_data[self._position:self._position + size]
        self._position += size
        return data

    def seek(self, offset, whence=0):
        if whence == 0:  # absolute file positioning
            self._position = offset
        elif whence == 1:  # seek relative to the current position
            self._position += offset
        elif whence == 2:  # seek relative to the file's end
            self._position = len(self._decompressed_data) + offset
        else:
            raise ValueError("Invalid value for whence")

        # Ensure the position is within bounds
        self._position = max(
            0, min(self._position, len(self._decompressed_data)))

    def tell(self):
        return self._position

    def flush(self):
        self.file.flush()

    def fileno(self):
        if hasattr(self.file, 'fileno'):
            return self.file.fileno()
        raise OSError("The underlying file object does not support fileno()")

    def isatty(self):
        if hasattr(self.file, 'isatty'):
            return self.file.isatty()
        return False

    def truncate(self, size=None):
        if hasattr(self.file, 'truncate'):
            return self.file.truncate(size)
        raise OSError("The underlying file object does not support truncate()")

    def close(self):
        if 'w' in self.mode or 'a' in self.mode or 'x' in self.mode:
            self.file.write(self._compressor.flush(zlib.Z_FINISH))
        if self.file_path:
            self.file.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


def _gzip_compress(data, compresslevel=9):
    """
    Compress data with a GZIP wrapper (wbits=31) in one shot.
    :param data: Bytes to compress.
    :param compresslevel: 1..9
    :return: GZIP-compressed bytes.
    """
    compobj = zlib.compressobj(compresslevel, zlib.DEFLATED, 31)
    cdata = compobj.compress(data)
    cdata += compobj.flush(zlib.Z_FINISH)
    return cdata


def _gzip_decompress(data):
    """
    Decompress data with gzip headers/trailers (wbits=31).
    Single-shot approach.
    :param data: GZIP-compressed bytes
    :return: Decompressed bytes
    """
    # If you need multi-member support, you'd need a streaming loop here.
    return zlib.decompress(data, 31)


def _gzip_decompress_multimember(data):
    """
    Decompress possibly multi-member GZIP data, returning all uncompressed bytes.

    - We loop over each GZIP member.
    - zlib.decompressobj(wbits=31) stops after the first member it encounters.
    - We use 'unused_data' to detect leftover data and continue until no more.
    """
    result = b""
    current_data = data

    while current_data:
        # Create a new decompress object for the next member
        dobj = zlib.decompressobj(31)
        try:
            part = dobj.decompress(current_data)
        except zlib.error as e:
            # If there's a decompression error, break or raise
            raise ValueError("Decompression error: {}".format(str(e)))

        result += part
        result += dobj.flush()

        if dobj.unused_data:
            # 'unused_data' holds the bytes after the end of this gzip member
            # So we move on to the next member
            current_data = dobj.unused_data
        else:
            # No leftover => we reached the end of the data
            break

    return result

class GzipFile(object):
    """
    A file-like wrapper that uses zlib at wbits=31 to mimic gzip compress/decompress,
    with multi-member support. Works on older Python versions (including Py2),
    where gzip.compress / gzip.decompress might be unavailable.

    - In read mode: loads entire file, checks GZIP magic if needed, and
      decompresses all members in a loop.
    - In write mode: buffers uncompressed data, then writes compressed bytes on close.
    - 'level' sets compression level (1..9).
    - Supports text ('t') vs binary modes.
    """

    # GZIP magic (first 2 bytes)
    GZIP_MAGIC = b'\x1f\x8b'

    def __init__(self, file_path=None, fileobj=None, mode='rb',
                 level=9, encoding=None, errors=None, newline=None):
        """
        :param file_path: Path to file on disk (optional)
        :param fileobj:  An existing file-like object (optional)
        :param mode: e.g. 'rb', 'wb', 'rt', 'wt', etc.
        :param level: Compression level (1..9)
        :param encoding: If 't' in mode, text encoding
        :param errors: Error handling for text encode/decode
        :param newline: Placeholder for signature compatibility
        """
        if file_path is None and fileobj is None:
            raise ValueError("Either file_path or fileobj must be provided")
        if file_path is not None and fileobj is not None:
            raise ValueError("Only one of file_path or fileobj should be provided")

        self.file_path = file_path
        self.fileobj = fileobj
        self.mode = mode
        self.level = level
        self.encoding = encoding
        self.errors = errors
        self.newline = newline

        # If reading, we store fully decompressed data in memory
        self._decompressed_data = b''
        self._position = 0

        # If writing, we store uncompressed data in memory, compress at close()
        self._write_buffer = b''

        # Text mode if 't' in mode
        self._text_mode = 't' in mode

        # Force binary file I/O mode
        internal_mode = mode.replace('t', 'b')

        if any(m in mode for m in ('w', 'a', 'x')):
            # Writing or appending
            if file_path:
                self.file = open(file_path, internal_mode)
            else:
                self.file = fileobj

        elif 'r' in mode:
            # Reading
            if file_path:
                if os.path.exists(file_path):
                    self.file = open(file_path, internal_mode)
                    self._load_file()
                else:
                    raise FileNotFoundError("No such file: '{}'".format(file_path))
            else:
                # fileobj
                self.file = fileobj
                self._load_file()
        else:
            raise ValueError("Mode should be 'rb'/'rt' or 'wb'/'wt'")

    def _load_file(self):
        """
        Read entire compressed file. Decompress all GZIP members.
        """
        self.file.seek(0)
        compressed_data = self.file.read()

        # (Optional) Check magic if you want to fail early on non-GZIP data
        # We'll do a quick check to see if it starts with GZIP magic
        if not compressed_data.startswith(self.GZIP_MAGIC):
            raise ValueError("Invalid GZIP header (magic bytes missing)")

        self._decompressed_data = _gzip_decompress_multimember(compressed_data)

        # If text mode, decode
        if self._text_mode:
            enc = self.encoding or 'UTF-8'
            err = self.errors or 'strict'
            self._decompressed_data = self._decompressed_data.decode(enc, err)

    def write(self, data):
        """
        Write data to our in-memory buffer.
        Actual compression (GZIP) occurs on close().
        """
        if 'r' in self.mode:
            raise IOError("File not open for writing")

        if self._text_mode:
            # Encode text to bytes
            data = data.encode(self.encoding or 'UTF-8', self.errors or 'strict')

        self._write_buffer += data

    def read(self, size=-1):
        """
        Read from the decompressed data buffer.
        """
        if 'r' not in self.mode:
            raise IOError("File not open for reading")

        if size < 0:
            size = len(self._decompressed_data) - self._position
        data = self._decompressed_data[self._position : self._position + size]
        self._position += size
        return data

    def seek(self, offset, whence=0):
        """
        Seek in the decompressed data buffer.
        """
        if 'r' not in self.mode:
            raise IOError("File not open for reading")

        if whence == 0:  # absolute
            new_pos = offset
        elif whence == 1:  # relative
            new_pos = self._position + offset
        elif whence == 2:  # from the end
            new_pos = len(self._decompressed_data) + offset
        else:
            raise ValueError("Invalid value for whence")

        self._position = max(0, min(new_pos, len(self._decompressed_data)))

    def tell(self):
        """
        Return the current position in the decompressed data buffer.
        """
        return self._position

    def flush(self):
        """
        Flush the underlying file, if possible.
        (No partial compression flush is performed here.)
        """
        if hasattr(self.file, 'flush'):
            self.file.flush()

    def fileno(self):
        """
        Return the file descriptor if available.
        """
        if hasattr(self.file, 'fileno'):
            return self.file.fileno()
        raise OSError("The underlying file object does not support fileno()")

    def isatty(self):
        """
        Return whether the underlying file is a TTY.
        """
        if hasattr(self.file, 'isatty'):
            return self.file.isatty()
        return False

    def truncate(self, size=None):
        """
        Truncate the underlying file if possible.
        """
        if hasattr(self.file, 'truncate'):
            return self.file.truncate(size)
        raise OSError("The underlying file object does not support truncate()")

    def close(self):
        """
        If in write mode, compress the entire buffer with wbits=31 (gzip) at the
        specified compression level, then write it out. Close file if we opened it.
        """
        if any(m in self.mode for m in ('w', 'a', 'x')):
            compressed = _gzip_compress(self._write_buffer, compresslevel=self.level)
            self.file.write(compressed)

        if self.file_path:
            self.file.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


class LzopFile(object):
    """
    A file-like wrapper around LZO compression/decompression using python-lzo.

    - In read mode (r): Reads the entire file, checks for LZOP magic bytes,
      then decompresses into memory.
    - In write mode (w/a/x): Buffers all data in memory. On close, writes
      the LZOP magic bytes + compressed data.
    - Supports a 'level' parameter (default=9). python-lzo commonly accepts only
      level=1 or level=9 for LZO1X_1 or LZO1X_999.
    """
    # LZOP magic bytes: b'\x89LZO\x0D\x0A\x1A\n'
    LZOP_MAGIC = b'\x89LZO\x0D\x0A\x1A\n'

    def __init__(self, file_path=None, fileobj=None, mode='rb',
                 level=9, encoding=None, errors=None, newline=None):
        """
        :param file_path: Path to the file (if any)
        :param fileobj: An existing file object (if any)
        :param mode: File mode, e.g., 'rb', 'wb', 'rt', 'wt', etc.
        :param level: Compression level (int). python-lzo typically supports 1 or 9.
        :param encoding: Text encoding (for text mode)
        :param errors: Error handling for encoding/decoding (e.g., 'strict')
        :param newline: Placeholder to mimic built-in open() signature
        """
        if file_path is None and fileobj is None:
            raise ValueError("Either file_path or fileobj must be provided")
        if file_path is not None and fileobj is not None:
            raise ValueError("Only one of file_path or fileobj should be provided")

        self.file_path = file_path
        self.fileobj = fileobj
        self.mode = mode
        self.level = level
        self.encoding = encoding
        self.errors = errors
        self.newline = newline
        self._decompressed_data = b''
        self._position = 0

        # For writing, store uncompressed data in memory until close()
        self._write_buffer = b''

        # Track whether we're doing text mode
        self._text_mode = 't' in mode

        # Force binary mode internally for file I/O
        internal_mode = mode.replace('t', 'b')

        if 'w' in mode or 'a' in mode or 'x' in mode:
            # Open the file if a path was specified; otherwise, use fileobj
            if file_path:
                self.file = open(file_path, internal_mode)
            else:
                self.file = fileobj

        elif 'r' in mode:
            # Reading
            if file_path:
                if os.path.exists(file_path):
                    self.file = open(file_path, internal_mode)
                    self._load_file()
                else:
                    raise FileNotFoundError("No such file: '{}'".format(file_path))
            else:
                # fileobj provided
                self.file = fileobj
                self._load_file()

        else:
            raise ValueError("Mode should be 'rb'/'rt' or 'wb'/'wt'")

    def _load_file(self):
        """
        Read the entire compressed file into memory. Expects LZOP magic bytes
        at the start. Decompress the remainder into _decompressed_data.
        """
        self.file.seek(0)
        compressed_data = self.file.read()

        # Check for the LZOP magic
        if not compressed_data.startswith(self.LZOP_MAGIC):
            raise ValueError("Invalid LZOP file header (magic bytes missing)")

        # Strip the magic; everything after is LZO-compressed data.
        compressed_data = compressed_data[len(self.LZOP_MAGIC):]

        # Decompress the remainder
        try:
            self._decompressed_data = lzo.decompress(compressed_data)
        except lzo.error as e:
            raise ValueError("LZO decompression failed: {}".format(str(e)))

        # If we're in text mode, decode from bytes to str
        if self._text_mode:
            enc = self.encoding or 'UTF-8'
            err = self.errors or 'strict'
            self._decompressed_data = self._decompressed_data.decode(enc, err)

    def write(self, data):
        """
        Write data into an internal buffer. The actual compression + file write
        happens on close().
        """
        if 'r' in self.mode:
            raise IOError("File not open for writing")

        if self._text_mode:
            # Encode data from str (Py3) or unicode (Py2) to bytes
            data = data.encode(self.encoding or 'UTF-8', self.errors or 'strict')

        # Accumulate in memory
        self._write_buffer += data

    def read(self, size=-1):
        """
        Read from the decompressed data buffer.
        """
        if 'r' not in self.mode:
            raise IOError("File not open for reading")

        if size < 0:
            size = len(self._decompressed_data) - self._position
        data = self._decompressed_data[self._position:self._position + size]
        self._position += size
        return data

    def seek(self, offset, whence=0):
        """
        Adjust the current read position in the decompressed buffer.
        """
        if 'r' not in self.mode:
            raise IOError("File not open for reading")

        if whence == 0:  # absolute
            new_pos = offset
        elif whence == 1:  # relative
            new_pos = self._position + offset
        elif whence == 2:  # relative to end
            new_pos = len(self._decompressed_data) + offset
        else:
            raise ValueError("Invalid value for whence")

        self._position = max(0, min(new_pos, len(self._decompressed_data)))

    def tell(self):
        """
        Return the current read position in the decompressed buffer.
        """
        return self._position

    def flush(self):
        """
        Flush the underlying file if supported. (No partial compression flush for LZO.)
        """
        if hasattr(self.file, 'flush'):
            self.file.flush()

    def fileno(self):
        """
        Return the file descriptor if available.
        """
        if hasattr(self.file, 'fileno'):
            return self.file.fileno()
        raise OSError("The underlying file object does not support fileno()")

    def isatty(self):
        """
        Return whether the underlying file is a TTY.
        """
        if hasattr(self.file, 'isatty'):
            return self.file.isatty()
        return False

    def truncate(self, size=None):
        """
        Truncate the underlying file if possible.
        """
        if hasattr(self.file, 'truncate'):
            return self.file.truncate(size)
        raise OSError("The underlying file object does not support truncate()")

    def close(self):
        """
        If in write mode, compress the entire accumulated buffer using LZO
        (with the specified level) and write it (with the LZOP magic) to the file.
        """
        if any(x in self.mode for x in ('w', 'a', 'x')):
            # Write the LZOP magic
            self.file.write(self.LZOP_MAGIC)

            # Compress the entire buffer
            try:
                # python-lzo supports level=1 or level=9 for LZO1X
                compressed = lzo.compress(self._write_buffer, self.level)
            except lzo.error as e:
                raise ValueError("LZO compression failed: {}".format(str(e)))

            self.file.write(compressed)

        if self.file_path:
            self.file.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


def open_compressed_file(filename):
    """ Open a file, trying various compression methods if available. """
    if filename.endswith('.gz'):
        return gzip.open(filename, 'rt', encoding='utf-8')
    elif filename.endswith('.bz2'):
        return bz2.open(filename, 'rt', encoding='utf-8')
    elif filename.endswith('.xz') or filename.endswith('.lzma'):
        if lzma:
            return lzma.open(filename, 'rt', encoding='utf-8')
        else:
            raise ImportError("lzma module is not available")
    elif filename.endswith('.zl') or filename.endswith('.zz'):
        return ZlibFile(file_path=filename, mode='rt')
    elif filename.endswith('.lzo') and "lzop" in compressionsupport:
        return LzopFile(file_path=filename, mode='rt')
    elif filename.endswith('.zst') and "zstandard" in compressionsupport:
        if 'zstandard' in sys.modules:
            return ZstdFile(file_path=filename, mode='rt')
        elif 'pyzstd' in sys.modules:
            return pyzstd.zstdfile.ZstdFile(filename, mode='rt')
        else:
            return Flase
    else:
        return io.open(filename, 'r', encoding='utf-8')

def save_compressed_file(data, filename):
    """ Save data to a file, using various compression methods if specified. """
    if filename.endswith('.gz'):
        with gzip.open(filename, 'wt', encoding='utf-8') as file:
            file.write(data)
    elif filename.endswith('.bz2'):
        with bz2.open(filename, 'wt', encoding='utf-8') as file:
            file.write(data)
    elif filename.endswith('.xz') or filename.endswith('.lzma'):
        if lzma:
            with lzma.open(filename, 'wt', encoding='utf-8') as file:
                file.write(data)
        else:
            raise ImportError("lzma module is not available")
    elif filename.endswith('.zl') or filename.endswith('.zz'):
        with ZlibFile(file_path=filename, mode='wb') as file:
            if isinstance(data, str):
                file.write(data.encode('utf-8'))
            else:
                file.write(data)
    elif filename.endswith('.lzo') and "lzop" in compressionsupport:
        with LzopFile(file_path=filename, mode='wb') as file:
            if isinstance(data, str):
                file.write(data.encode('utf-8'))
            else:
                file.write(data)
    elif filename.endswith('.zst') and "zstandard" in compressionsupport:
        if 'zstandard' in sys.modules:
            with ZstdFile(file_path=filename, mode='wb') as file:
                if isinstance(data, str):
                    file.write(data.encode('utf-8'))
                else:
                    file.write(data)
        elif 'pyzstd' in sys.modules:
            with pyzstd.zstdfile.ZstdFile(filename, mode='wb') as file:
                if isinstance(data, str):
                    file.write(data.encode('utf-8'))
                else:
                    file.write(data)
        else:
            return Flase
    else:
        with io.open(filename, 'w', encoding='utf-8') as file:
            file.write(data)

def parse_archive(content):
    """Properly parse the archive format maintaining all hierarchical data"""
    data = OrderedDict()
    stack = []
    current = data
    current_section = None
    current_key = None
    body_mode = False
    body_content = []
    body_name = None
    
    lines = content.split('\n')
    
    for line in lines:
        line = line.rstrip()
        
        # Check for section markers
        start_match = re.match(r'^--- Start (.*) ---$', line)
        end_match = re.match(r'^--- End (.*) ---$', line)
        
        if start_match:
            section_name = start_match.group(1)
            
            # Handle body sections
            if 'Body' in section_name:
                body_mode = True
                body_name = section_name.replace(' Body', '')
                body_content = []
                continue
            
            # Create new section container
            new_section = OrderedDict()
            if current_section is None:
                # Top-level section
                if section_name not in data:
                    data[section_name] = []
                data[section_name].append(new_section)
            else:
                # Nested section
                if current_section not in current:
                    current[current_section] = []
                current[current_section].append(new_section)
            
            # Push current context to stack
            stack.append((current, current_section))
            current = new_section
            current_section = None
            continue
            
        if end_match:
            section_name = end_match.group(1)
            
            # Handle body sections
            if 'Body' in section_name:
                body_mode = False
                if body_name and body_content:
                    # Remove trailing empty lines
                    while body_content and not body_content[-1].strip():
                        body_content.pop()
                    current[body_name] = '\n'.join(body_content)
                body_name = None
                body_content = []
                continue
            
            # Pop context from stack
            if stack:
                current, current_section = stack.pop()
            continue
            
        # Handle body content
        if body_mode:
            body_content.append(line)
            continue
            
        # Handle key-value pairs
        if ': ' in line:
            key, value = line.split(': ', 1)
            current_key = key
            current_section = None
            current[key] = value
        elif line.endswith(':'):
            current_key = line[:-1]
            current_section = None
            current[current_key] = ''
        elif current_key and line.strip():
            # Append to previous value
            current[current_key] += '\n' + line
        elif line.strip():
            # Potential section name without key-value pair
            current_section = line.strip()
    
    return data

def parse_file(filename, validate_only=False, verbose=False):
    with open_compressed_file(filename) as file:
        lines = file.read()
    return parse_archive(lines)

def parse_string(data, validate_only=False, verbose=False):
    lines = StringIO(data).read()
    return parse_archive(lines)

def generate_archive(data):
    """Generate the archive format from the structured data"""
    output = []
    
    def process_section(section, name):
        output.append('--- Start {} ---'.format(name))
        
        for key, value in section.items():
            if isinstance(value, OrderedDict):
                process_section(value, key)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, (OrderedDict, dict)):
                        process_section(item, key)
                    else:
                        output.append('{}: {}'.format(key, item))
            elif '\n' in str(value):
                output.append('{}:'.format(key))
                output.append('--- Start {} Body ---'.format(key))
                output.append(value)
                output.append('--- End {} Body ---'.format(key))
            else:
                output.append('{}: {}'.format(key, value))
        
        output.append('--- End {} ---'.format(name))
    
    for section_name, section_data in data.items():
        if isinstance(section_data, list):
            for item in section_data:
                if isinstance(item, (OrderedDict, dict)):
                    process_section(item, section_name)
                else:
                    output.append('{}: {}'.format(section_name, item))
        else:
            process_section(section_data, section_name)
    
    return '\n'.join(output)

def services_to_string(services):
    return generate_archive(services)

def services_to_string_from_file(filename):
    services = parse_file(filename, False, False);
    return services_to_string(services)

def save_services_to_file(services, filename):
    """
    Save services to a file, inferring compression by extension (Python 2/3 compatible).
    """
    data = generate_archive(services)
    save_compressed_file(data, filename)

def save_services_to_file_from_file(filename, outfilename):
    services = parse_file(filename, False, False);
    return save_services_to_file(services, outfilename)

class CompressionError(Exception):
    """Custom exception for compression-related errors"""
    pass

def display_services(services):
    """Display the archive services data in a human-readable format (Python 2/3 compatible)."""
    if isinstance(services, dict):  # Handle single service case
        services = [services]
    
    for service in services:
        print("\n--- Service Entry {0} ---".format(service.get('Entry', '')))
        print("Service: {0}".format(service.get('Service', '')))
        print("TimeZone: {0}".format(service.get('TimeZone', 'UTC')))
        
        # Display Info Body if present
        if 'Info' in service and service['Info']:
            info_body = service['Info'].get('InfoBody', '').strip()
            if info_body:
                print("\nInfo:")
                print("  {0}".format(info_body.replace('\n', '\n  ')))
        
        # Display User List
        if 'UserList' in service and service['UserList']:
            print("\nUsers:")
            for user_info in service['UserList']:
                print("  User {0}:".format(user_info.get('User', '')))
                print("    Name: {0}".format(user_info.get('Name', '')))
                print("    Handle: {0}".format(user_info.get('Handle', '')))
                print("    Location: {0}".format(user_info.get('Location', '')))
                print("    Joined: {0}".format(user_info.get('Joined', '')))
                print("    Birthday: {0}".format(user_info.get('Birthday', '')))
                
                # Display Bio if present
                if 'Bio' in user_info and user_info['Bio']:
                    bio_body = user_info['Bio'].get('BioBody', '').strip()
                    if bio_body:
                        print("    Bio: {0}".format(bio_body.replace('\n', '\n      ')))
        
        # Display Categorization
        if 'CategorizationList' in service and service['CategorizationList']:
            print("\nCategories:")
            categories = service['CategorizationList'].get('Categories', [])
            forums = service['CategorizationList'].get('Forums', [])
            
            if categories:
                print("  Categories: {0}".format(', '.join(categories)))
            if forums:
                print("  Forums: {0}".format(', '.join(forums)))
            
            # Display Category List details
            for category in service['CategorizationList'].get('CategoryList', []):
                print("\n  Category:")
                print("    Kind: {0}".format(category.get('Kind', '')))
                print("    ID: {0}".format(category.get('ID', '0')))
                print("    InSub: {0}".format(category.get('InSub', '0')))
                print("    Headline: {0}".format(category.get('Headline', '')))
                
                # Display Description if present
                if 'Description' in category and category['Description']:
                    desc_body = category['Description'].get('DescriptionBody', '').strip()
                    if desc_body:
                        print("    Description: {0}".format(desc_body.replace('\n', '\n      ')))
        
        # Display Message Threads
        if 'MessageList' in service and service['MessageList']:
            print("\nMessage Threads:")
            interactions = service['MessageList'].get('Interactions', [])
            status = service['MessageList'].get('Status', [])
            
            if interactions:
                print("  Supported Interactions: {0}".format(', '.join(interactions)))
            if status:
                print("  Status: {0}".format(', '.join(status)))
            
            for thread in service['MessageList'].get('MessageThread', []):
                print("\n  Thread {0}:".format(thread.get('Thread', '0')))
                print("    Title: {0}".format(thread.get('Title', '')))
                print("    Type: {0}".format(thread.get('Type', '')))
                print("    State: {0}".format(thread.get('State', '')))
                if 'Category' in thread:
                    print("    Category: {0}".format(thread['Category']))
                if 'Forum' in thread:
                    print("    Forum: {0}".format(thread['Forum']))
                if 'Keywords' in thread:
                    print("    Keywords: {0}".format(thread['Keywords']))
                
                # Display Messages in thread
                for msg in thread.get('MessagePost', []):
                    print("\n    {0} at {1} on {2}:".format(
                        msg.get('Author', ''),
                        msg.get('Time', ''),
                        msg.get('Date', '')))
                    print("      Type: {0}".format(msg.get('SubType', 'Post' if msg.get('Post') == 1 else 'Reply')))
                    print("      Post ID: {0}".format(msg.get('Post', 0)))
                    print("      Nested Level: {0}".format(msg.get('Nested', 0)))
                    
                    # Display Message Body
                    if 'Message' in msg and msg['Message']:
                        msg_body = msg['Message'].get('MessageBody', '').strip()
                        if msg_body:
                            print("      Message: {0}".format(msg_body.replace('\n', '\n        ')))
                    
                    # Display Polls if present
                    if 'Polls' in msg and msg['Polls']:
                        for poll in msg['Polls'].get('PollBody', []):
                            print("\n      Poll:")
                            print("        Question: {0}".format(poll.get('Question', '')))
                            print("        Answers: {0}".format(', '.join(poll.get('Answers', []))))
                            print("        Results: {0}".format(', '.join(str(r) for r in poll.get('Results', []))))
                            print("        Percentage: {0}".format(', '.join(str(p) for p in poll.get('Percentage', []))))
                            print("        Votes: {0}".format(poll.get('Votes', '')))
        
        print("\n" + "="*50 + "\n")

def display_services_from_file(filename):
    services = parse_file(filename, False, False);
    return display_services(services)

def services_to_html(services):
    """
    Render the services list as a styled HTML document string (Python 2/3 compatible).

    Args:
        services (list of dict): Parsed services data structure.

    Returns:
        str: A complete HTML page.
    """
    if not isinstance(services, list):  # Handle single service case
        services = [services]

    lines = []
    # Document head
    lines.append('<!DOCTYPE html>')
    lines.append('<html lang="en">')
    lines.append('<head>')
    lines.append('  <meta charset="UTF-8">')
    lines.append('  <meta name="viewport" content="width=device-width, initial-scale=1.0">')
    lines.append('  <title>Services Report</title>')
    lines.append('  <style>')
    lines.append('    body { font-family: Arial, sans-serif; margin: 20px; background: #f9f9f9; }')
    lines.append('    .service-card { background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 16px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }')
    lines.append('    .service-card h2 { margin-top: 0; color: #333; }')
    lines.append('    .thread-card { background: #fafafa; border-left: 4px solid #007BFF; padding: 12px; margin: 10px 0; }')
    lines.append('    .message-list { list-style: none; padding-left: 0; }')
    lines.append('    .message-list li { margin-bottom: 10px; }')
    lines.append('    .poll-card { background: #f0f8ff; border: 1px solid #cce; border-radius: 4px; padding: 10px; margin: 10px 0; }')
    lines.append('  </style>')
    lines.append('</head>')
    lines.append('<body>')
    lines.append('<div class="services-container">')

    # Service cards
    for svc in services:
        entry = svc.get('Entry', '')
        name = svc.get('Service', '')
        lines.append('<div class="service-card">')
        lines.append('  <h2>Service Entry: {0} &mdash; {1}</h2>'.format(
            escape(unicode_type(entry)), escape(unicode_type(name))))

        # Info
        info = svc.get('Info', {}).get('InfoBody', '').strip()
        if info:
            lines.append('  <p><strong>Info:</strong> <blockquote style="white-space: pre-wrap;">{0}</blockquote></p>'.format(
                escape(unicode_type(info))))

        # Interactions & Status
        interactions = svc.get('Interactions', [])
        if interactions:
            items = ', '.join(escape(unicode_type(i)) for i in interactions)
            lines.append('  <p><strong>Interactions:</strong> {0}</p>'.format(items))
        status = svc.get('Status', [])
        if status:
            items = ', '.join(escape(unicode_type(s)) for s in status)
            lines.append('  <p><strong>Status:</strong> {0}</p>'.format(items))

        # Categories
        cats = svc.get('Categories', [])
        if cats:
            lines.append('  <h3>Categories</h3>')
            lines.append('  <ul>')
            for cat in cats:
                headline = cat.get('Headline', '')
                level = cat.get('Level', '')
                lines.append('    <li>{0} (<em>{1}</em>)</li>'.format(
                    escape(unicode_type(headline)), escape(unicode_type(level))))
            lines.append('  </ul>')

        # Users
        users = svc.get('UserList', [])
        if users:
            lines.append('  <h3>Users</h3>')
            lines.append('  <ul>')
            for user in users:
                uid = user.get('User', '')
                uname = user.get('Name', '')
                handle = user.get('Handle', '')
                bio = user.get('Bio', {}).get('BioBody', '').strip()
                lines.append('    <li><strong>{0}</strong>: {1} ({2})</li>'.format(
                    escape(unicode_type(uid)), escape(unicode_type(uname)), escape(unicode_type(handle))))
                if bio:
                    lines.append('      <blockquote style="white-space: pre-wrap;">{0}</blockquote>'.format(
                        escape(unicode_type(bio))))
            lines.append('  </ul>')

        # Message Threads
        threads = svc.get('MessageList', {}).get('MessageThread', [])
        if threads:
            lines.append('  <h3>Message Threads</h3>')
            for th in threads:
                title = th.get('Title', '')
                lines.append('  <div class="thread-card">')
                lines.append('    <h4>{0}</h4>'.format(
                    escape(unicode_type(title))))

                msgs = th.get('MessagePost', [])
                if msgs:
                    lines.append('    <ul class="message-list">')
                    for msg in msgs:
                        author = msg.get('Author', '')
                        body = msg.get('Message', {}).get('MessageBody', '').strip()
                        lines.append('      <li><strong>{0}</strong>: <blockquote style="white-space: pre-wrap;">{1}</blockquote></li>'.format(
                            escape(unicode_type(author)), escape(unicode_type(body))))
                        
                        # Polls
                        if 'Polls' in msg and msg['Polls']:
                            for poll in msg['Polls'].get('PollBody', []):
                                lines.append('      <div class="poll-card">')
                                lines.append('        <strong>Poll:</strong> {0}'.format(
                                    escape(unicode_type(poll.get('Question', '')))))
                                lines.append('        <ul>')
                                for ans, res, perc in zip(
                                    poll.get('Answers', []),
                                    poll.get('Results', []),
                                    poll.get('Percentage', [])):
                                    lines.append('          <li>{0}: {1} ({2}%)</li>'.format(
                                        escape(unicode_type(ans)),
                                        escape(unicode_type(res)),
                                        escape(unicode_type(perc))))
                                lines.append('        </ul>')
                                lines.append('        <div>Total votes: {0}</div>'.format(
                                    escape(unicode_type(poll.get('Votes', '')))))
                                lines.append('      </div>')
                    lines.append('    </ul>')
                lines.append('  </div>')

        lines.append('</div>')

    lines.append('</div>')
    lines.append('</body>')
    lines.append('</html>')

    return '\n'.join(lines)

def services_to_html_from_file(filename):
    services = parse_file(filename, False, False);
    return services_to_html(services)

def save_services_to_html_file(services, filename):
    """
    Generate styled HTML from services and save to the given filename.
    Works on both Python 2 and 3.

    Args:
        services (list of dict): Parsed services.
        filename (str): Path to write the HTML file.
    """
    html_content = services_to_html(services)
    # Use io.open for Py2/3 compatibility
    save_compressed_file(html_content, filename)

def save_services_to_html_file_from_file(filename, outfilename):
    services = parse_file(filename, False, False);
    return save_services_to_html_file(services, outfilename)

# Serialization functions with improved type hints and error handling

def to_json(data, indent = 2, ensure_ascii = False):
    """Convert data to a JSON string."""
    return json.dumps(data, indent=indent, ensure_ascii=ensure_ascii)

def from_json(json_str):
    """Convert a JSON string back to Python data."""
    return json.loads(json_str)

def load_from_json_file(filename):
    """Load data from a JSON file."""
    with open_compressed_file(filename, 'rt', encoding='utf-8') as file:
        return json.load(file)

def save_to_json_file(data, filename, indent = 2, ensure_ascii = False):
    """Save data to a JSON file."""
    json_data = to_json(data, indent, ensure_ascii)
    save_compressed_file(json_data, filename)

def to_yaml(data):
    """Convert data to a YAML string if PyYAML is available."""
    if not HAS_YAML:
        return False
    return yaml.safe_dump(data, default_flow_style=False, allow_unicode=True)

def from_yaml(yaml_str) :
    """Convert a YAML string to Python data if PyYAML is available."""
    if not HAS_YAML:
        return False
    return yaml.safe_load(yaml_str)

def load_from_yaml_file(filename):
    """Load data from a YAML file if PyYAML is available."""
    if not HAS_YAML:
        return False
    with open_compressed_file(filename, 'rt', encoding='utf-8') as file:
        return yaml.safe_load(file)

def save_to_yaml_file(data, filename):
    """Save data to a YAML file if PyYAML is available."""
    if not HAS_YAML:
        return False
    yaml_data = to_yaml(data)
    if yaml_data is False:
        return False
    save_compressed_file(yaml_data, filename)
    return True

def to_marshal(data):
    """Convert data to a marshaled byte string."""
    return marshal.dumps(data)

def from_marshal(marshal_bytes):
    """Convert a marshaled byte string back to Python data."""
    return marshal.loads(marshal_bytes)

def load_from_marshal_file(filename):
    """Load data from a marshal file."""
    with open_compressed_file(filename, 'rb') as file:
        return marshal.load(file)

def save_to_marshal_file(data, filename):
    """Save data to a marshal file."""
    marshal_data = to_marshal(data)
    save_compressed_file(marshal_data, filename, 'wb')

def to_pickle(data, protocol = pickle.HIGHEST_PROTOCOL) -> bytes:
    """Convert data to a pickled byte string."""
    return pickle.dumps(data, protocol=protocol)

def from_pickle(pickle_bytes):
    """Convert a pickled byte string back to Python data."""
    return pickle.loads(pickle_bytes)

def load_from_pickle_file(filename):
    """Load data from a pickle file."""
    with open_compressed_file(filename, 'rb') as file:
        return pickle.load(file)

def save_to_pickle_file(data, filename, protocol = pickle.HIGHEST_PROTOCOL):
    """Save data to a pickle file."""
    pickle_data = to_pickle(data, protocol)
    save_compressed_file(pickle_data, filename, 'wb')

def to_array(data):
    """Convert data to a string representation using Python literal syntax."""
    return repr(data)

def from_array(data_str):
    """Convert a string (Python literal) back to data using safe evaluation."""
    return ast.literal_eval(data_str)

def load_from_array_file(filename):
    """Load data from a file containing Python literal syntax."""
    with open_compressed_file(filename, 'rt', encoding='utf-8') as file:
        return ast.literal_eval(file.read())

def save_to_array_file(data, filename):
    """Save data to a file using Python literal syntax."""
    data_str = to_array(data)
    save_compressed_file(data_str, filename)

def main():
    # Example usage
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            content = f.read()
    else:
        content = sys.stdin.read()
    
    # Parse the archive
    parsed_data = parse_archive(content)
    
    # Convert to JSON
    json_str = to_json(parsed_data, indent=2)
    print("\nJSON Representation:")
    print(json_str)
    
    # Convert back from JSON
    reconstructed_data = from_json(json_str)
    
    # Regenerate archive format
    regenerated = generate_archive(reconstructed_data)
    
    # Verify round trip
    print("\nOriginal == Regenerated?", content.strip() == regenerated.strip())
    
    # Example access
    if 'User List' in parsed_data:
        print("\nUsers:")
        for user in parsed_data['User List']:
            print("- {} (@{})".format(user.get('Name', ''), user.get('Handle', '')))
    
    if 'Message List' in parsed_data:
        print("\nThreads:")
        for thread in parsed_data['Message List']:
            print("- {} ({} posts)".format(thread.get('Title', ''), 
                  len([k for k in thread.keys() if k.startswith('Post')])))

if __name__ == '__main__':
    main()
