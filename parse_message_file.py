#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals, generators, with_statement, nested_scopes
import platform
import logging
import marshal
import pickle
import json
import zlib
import sys
import ast
import os
import io
import re

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

try:
    from html.parser import HTMLParser
except ImportError:
    from HTMLParser import HTMLParser

# FTP Support
ftpssl = True
try:
    from ftplib import FTP, FTP_TLS
except ImportError:
    ftpssl = False
    from ftplib import FTP

try:
    basestring
except NameError:
    basestring = str

# URL Parsing
try:
    from urllib.parse import urlparse, urlunparse
except ImportError:
    from urlparse import urlparse, urlunparse

# Paramiko support
haveparamiko = False
try:
    import paramiko
    haveparamiko = True
except ImportError:
    pass

# PySFTP support
havepysftp = False
try:
    import pysftp
    havepysftp = True
except ImportError:
    pass

# Add the mechanize import check
havemechanize = False
try:
    import mechanize
    havemechanize = True
except ImportError:
    pass
except OSError:
    pass

# Requests support
haverequests = False
try:
    import requests
    haverequests = True
    import urllib3
    logging.getLogger("urllib3").setLevel(logging.WARNING)
except ImportError:
    pass

# HTTPX support
havehttpx = False
try:
    import httpx
    havehttpx = True
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
except ImportError:
    pass

# HTTP and URL parsing
try:
    from urllib.request import Request, build_opener, HTTPBasicAuthHandler
    from urllib.parse import urlparse
except ImportError:
    from urllib2 import Request, build_opener, HTTPBasicAuthHandler
    from urlparse import urlparse

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


__use_pysftp__ = False
if(not havepysftp):
    __use_pysftp__ = False
__use_http_lib__ = "httpx"
if(__use_http_lib__ == "httpx" and haverequests and not havehttpx):
    __use_http_lib__ = "requests"
if(__use_http_lib__ == "requests" and havehttpx and not haverequests):
    __use_http_lib__ = "httpx"
if((__use_http_lib__ == "httpx" or __use_http_lib__ == "requests") and not havehttpx and not haverequests):
    __use_http_lib__ = "urllib"


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
__version_info__ = (0, 1, 6, "RC 1", 1);
__version_date_info__ = (2025, 7, 19, "RC 1", 1);
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


PyBitness = platform.architecture()
if(PyBitness == "32bit" or PyBitness == "32"):
    PyBitness = "32"
elif(PyBitness == "64bit" or PyBitness == "64"):
    PyBitness = "64"
else:
    PyBitness = "32"


geturls_ua_python = "Mozilla/5.0 (compatible; {proname}/{prover}; +{prourl})".format(
    proname=__project__, prover=__version__, prourl=__project_url__)
if(platform.python_implementation() != ""):
    py_implementation = platform.python_implementation()
if(platform.python_implementation() == ""):
    py_implementation = "Python"
geturls_ua_python_alt = "Mozilla/5.0 ({osver}; {archtype}; +{prourl}) {pyimp}/{pyver} (KHTML, like Gecko) {proname}/{prover}".format(osver=platform.system(
)+" "+platform.release(), archtype=platform.machine(), prourl=__project_url__, pyimp=py_implementation, pyver=platform.python_version(), proname=__project__, prover=__version__)
geturls_ua_googlebot_google = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
geturls_ua_googlebot_google_old = "Googlebot/2.1 (+http://www.google.com/bot.html)"
geturls_headers_upcean_python = {'Referer': "http://google.com/", 'User-Agent': geturls_ua_python, 'Accept-Encoding': "none", 'Accept-Language': "en-US,en;q=0.8,en-CA,en-GB;q=0.6", 'Accept-Charset': "ISO-8859-1,ISO-8859-15,utf-8;q=0.7,*;q=0.7", 'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 'Connection': "close",
                                    'SEC-CH-UA': "\""+__project__+"\";v=\""+str(__version__)+"\", \"Not;A=Brand\";v=\"8\", \""+py_implementation+"\";v=\""+str(platform.release())+"\"", 'SEC-CH-UA-FULL-VERSION': str(__version__), 'SEC-CH-UA-PLATFORM': ""+py_implementation+"", 'SEC-CH-UA-ARCH': ""+platform.machine()+"", 'SEC-CH-UA-PLATFORM': str(__version__), 'SEC-CH-UA-BITNESS': str(PyBitness)}
geturls_headers_upcean_python_alt = {'Referer': "http://google.com/", 'User-Agent': geturls_ua_python_alt, 'Accept-Encoding': "none", 'Accept-Language': "en-US,en;q=0.8,en-CA,en-GB;q=0.6", 'Accept-Charset': "ISO-8859-1,ISO-8859-15,utf-8;q=0.7,*;q=0.7", 'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 'Connection': "close",
                                        'SEC-CH-UA': "\""+__project__+"\";v=\""+str(__version__)+"\", \"Not;A=Brand\";v=\"8\", \""+py_implementation+"\";v=\""+str(platform.release())+"\"", 'SEC-CH-UA-FULL-VERSION': str(__version__), 'SEC-CH-UA-PLATFORM': ""+py_implementation+"", 'SEC-CH-UA-ARCH': ""+platform.machine()+"", 'SEC-CH-UA-PLATFORM': str(__version__), 'SEC-CH-UA-BITNESS': str(PyBitness)}
geturls_headers_googlebot_google = {'Referer': "http://google.com/", 'User-Agent': geturls_ua_googlebot_google, 'Accept-Encoding': "none", 'Accept-Language': "en-US,en;q=0.8,en-CA,en-GB;q=0.6",
                                    'Accept-Charset': "ISO-8859-1,ISO-8859-15,utf-8;q=0.7,*;q=0.7", 'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 'Connection': "close"}
geturls_headers_googlebot_google_old = {'Referer': "http://google.com/", 'User-Agent': geturls_ua_googlebot_google_old, 'Accept-Encoding': "none", 'Accept-Language': "en-US,en;q=0.8,en-CA,en-GB;q=0.6",
                                        'Accept-Charset': "ISO-8859-1,ISO-8859-15,utf-8;q=0.7,*;q=0.7", 'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 'Connection': "close"}


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

def parse_line(line):
    """ Parse a line in the format 'var: value' and return the key and value. """
    parts = line.split(":", 1)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    return None, None

def validate_non_negative_integer(value, key, line_number):
    """ Utility to validate that a given value is a non-negative integer """
    try:
        int_value = int(value)
        if int_value < 0:
            raise ValueError("Negative value '{0}' for key '{1}' on line {2}".format(value, key, line_number))
        return int_value
    except ValueError as e:
        raise ValueError("Invalid integer '{0}' for key '{1}' on line {2}".format(value, key, line_number))


def parse_file(filename, validate_only=False, verbose=False):
    with open_compressed_file(filename) as file:
        lines = file.readlines()
    return parse_lines(lines, validate_only, verbose)

def parse_string(data, validate_only=False, verbose=False):
    lines = StringIO(data).readlines()
    return parse_lines(lines, validate_only, verbose)


def parse_lines(lines, validate_only=False, verbose=False):
    services = []
    current_service = None
    in_section = {
        'user_list': False,
        'message_list': False,
        'message_thread': False,
        'user_info': False,
        'message_post': False,
        'bio_body': False,
        'signature_body': False,
        'message_body': False,
        'comment_section': False,
        'include_service': False,
        'include_users': False,
        'include_messages': False,
        'category_list': False,
        'description_body': False,
        'include_categories': False,
        'categorization_list': False,
        'info_body': False,
        'poll_list': False,
        'poll_body': False,
    }
    include_files = []
    user_id = None
    current_bio = None
    current_message = None
    current_thread = None
    current_category = None
    current_info = None
    current_poll = None
    current_polls = []
    categorization_values = {'Categories': [], 'Forums': []}
    category_ids = {'Categories': [], 'Forums': []}
    post_id = 1

    def parse_include_files(file_list):
        included_services = []
        for include_file in file_list:
            included_services.extend(parse_file(include_file, validate_only, verbose))
        return included_services

    def parse_include_users(file_list):
        users = {}
        for include_file in file_list:
            included_users = parse_file(include_file, validate_only, verbose)
            for service in included_users:
                users.update(service['Users'])
        return users

    def parse_include_messages(file_list):
        messages = []
        for include_file in file_list:
            included_messages = parse_file(include_file, validate_only, verbose)
            for service in included_messages:
                messages.extend(service['MessageThreads'])
        return messages

    def parse_include_categories(file_list):
        categories = []
        for include_file in file_list:
            included_categories = parse_file(include_file, validate_only, verbose)
            for service in included_categories:
                categories.extend(service['Categories'])
        return categories

    try:
        for line_number, line in enumerate(lines, 1):
            line = line.strip()
            if line == "--- Include Service Start ---":
                in_section['include_service'] = True
                include_files = []
                if verbose:
                    print("Line {0}: {1} (Starting include service section)".format(line_number, line))
                continue
            elif line == "--- Include Service End ---":
                in_section['include_service'] = False
                if verbose:
                    print("Line {0}: {1} (Ending include service section)".format(line_number, line))
                services.extend(parse_include_files(include_files))
                continue
            elif in_section['include_service']:
                include_files.append(line)
                if verbose:
                    print("Line {0}: {1} (Including file for service)".format(line_number, line))
                continue
            elif line == "--- Include Users Start ---":
                in_section['include_users'] = True
                include_files = []
                if verbose:
                    print("Line {0}: {1} (Starting include users section)".format(line_number, line))
                continue
            elif line == "--- Include Users End ---":
                in_section['include_users'] = False
                if verbose:
                    print("Line {0}: {1} (Ending include users section)".format(line_number, line))
                if current_service:
                    current_service['Users'].update(parse_include_users(include_files))
                continue
            elif in_section['include_users']:
                include_files.append(line)
                if verbose:
                    print("Line {0}: {1} (Including file for users)".format(line_number, line))
                continue
            elif line == "--- Include Messages Start ---":
                in_section['include_messages'] = True
                include_files = []
                if verbose:
                    print("Line {0}: {1} (Starting include messages section)".format(line_number, line))
                continue
            elif line == "--- Include Messages End ---":
                in_section['include_messages'] = False
                if verbose:
                    print("Line {0}: {1} (Ending include messages section)".format(line_number, line))
                if current_service:
                    current_service['MessageThreads'].extend(parse_include_messages(include_files))
                continue
            elif in_section['include_messages']:
                include_files.append(line)
                if verbose:
                    print("Line {0}: {1} (Including file for messages)".format(line_number, line))
                continue
            elif line == "--- Include Categories Start ---":
                in_section['include_categories'] = True
                include_files = []
                if verbose:
                    print("Line {0}: {1} (Starting include categories section)".format(line_number, line))
                continue
            elif line == "--- Include Categories End ---":
                in_section['include_categories'] = False
                if verbose:
                    print("Line {0}: {1} (Ending include categories section)".format(line_number, line))
                if current_service:
                    current_service['Categories'].extend(parse_include_categories(include_files))
                    for category in current_service['Categories']:
                        kind_split = category.get('Kind', '').split(",")
                        category['Type'] = kind_split[0].strip() if len(kind_split) > 0 else ""
                        category['Level'] = kind_split[1].strip() if len(kind_split) > 1 else ""
                        category_ids[category['Type']].append(category['ID'])
                continue
            elif in_section['include_categories']:
                include_files.append(line)
                if verbose:
                    print("Line {0}: {1} (Including file for categories)".format(line_number, line))
                continue
            elif line == "--- Start Archive Service ---":
                current_service = {'Users': {}, 'MessageThreads': [], 'Categories': [], 'Interactions': [], 'Categorization': {}, 'Info': ''}
                if verbose:
                    print("Line {0}: {1} (Starting new archive service)".format(line_number, line))
                continue
            elif line == "--- End Archive Service ---":
                services.append(current_service)
                current_service = None
                if verbose:
                    print("Line {0}: {1} (Ending archive service)".format(line_number, line))
                continue
            elif line == "--- Start Comment Section ---":
                in_section['comment_section'] = True
                if verbose:
                    print("Line {0}: {1} (Starting comment section)".format(line_number, line))
                continue
            elif line == "--- End Comment Section ---":
                in_section['comment_section'] = False
                if verbose:
                    print("Line {0}: {1} (Ending comment section)".format(line_number, line))
                continue
            elif in_section['comment_section']:
                if verbose:
                    print("Line {0}: {1} (Comment)".format(line_number, line))
                continue
            elif line == "--- Start Category List ---":
                in_section['category_list'] = True
                current_category = {}
                if verbose:
                    print("Line {0}: {1} (Starting category list)".format(line_number, line))
                continue
            elif line == "--- End Category List ---":
                in_section['category_list'] = False
                if current_category:
                    kind_split = current_category.get('Kind', '').split(",")
                    current_category['Type'] = kind_split[0].strip() if len(kind_split) > 0 else ""
                    current_category['Level'] = kind_split[1].strip() if len(kind_split) > 1 else ""
                    if current_category['Type'] not in categorization_values:
                        raise ValueError("Invalid 'Type' value '{0}' on line {1}. Expected one of {2}.".format(current_category['Type'], line_number, categorization_values.keys()))
                    if current_category['InSub'] != 0 and current_category['InSub'] not in category_ids[current_category['Type']]:
                        raise ValueError("InSub value '{0}' on line {1} does not match any existing ID values.".format(current_category['InSub'], line_number))
                    current_service['Categories'].append(current_category)
                    category_ids[current_category['Type']].append(current_category['ID'])
                current_category = None
                if verbose:
                    print("Line {0}: {1} (Ending category list)".format(line_number, line))
                continue
            elif line == "--- Start Categorization List ---":
                in_section['categorization_list'] = True
                current_service['Categorization'] = {}
                if verbose:
                    print("Line {0}: {1} (Starting categorization list)".format(line_number, line))
                continue
            elif line == "--- End Categorization List ---":
                in_section['categorization_list'] = False
                if verbose:
                    print("Line {0}: {1} (Ending categorization list)".format(line_number, line))
                categorization_values = current_service['Categorization']
                continue
            elif line == "--- Start Info Body ---":
                in_section['info_body'] = True
                if current_service:
                    current_info = []
                    if verbose:
                        print("Line {0}: {1} (Starting info body)".format(line_number, line))
                continue
            elif line == "--- End Info Body ---":
                in_section['info_body'] = False
                if current_service and current_info is not None:
                    current_service['Info'] = "\n".join(current_info)
                    current_info = None
                    if verbose:
                        print("Line {0}: {1} (Ending info body)".format(line_number, line))
                continue
            elif in_section['info_body']:
                if current_service and current_info is not None:
                    current_info.append(line)
                if verbose:
                    print("Line {0}: {1}".format(line_number, line))
                continue
            elif line == "--- Start Poll List ---":
                in_section['poll_list'] = True
                current_polls = []
                if verbose:
                    print("Line {0}: {1} (Starting poll list)".format(line_number, line))
                continue
            elif line == "--- End Poll List ---":
                in_section['poll_list'] = False
                if current_message:
                    current_message['Polls'] = current_polls
                if verbose:
                    print("Line {0}: {1} (Ending poll list)".format(line_number, line))
                continue
            elif in_section['poll_list'] and line == "--- Start Poll Body ---":
                in_section['poll_body'] = True
                current_poll = {}
                if verbose:
                    print("Line {0}: {1} (Starting poll body)".format(line_number, line))
                continue
            elif in_section['poll_body'] and line == "--- End Poll Body ---":
                in_section['poll_body'] = False
                if current_poll is not None:
                    current_polls.append(current_poll)
                    current_poll = None
                if verbose:
                    print("Line {0}: {1} (Ending poll body)".format(line_number, line))
                continue
            elif in_section['poll_body']:
                key, value = parse_line(line)
                if key and current_poll is not None:
                    if key in ['Answers', 'Results', 'Percentage']:
                        current_poll[key] = [item.strip() for item in value.split(',')]
                    else:
                        current_poll[key] = value
                continue
            elif current_service is not None:
                key, value = parse_line(line)
                if key == "Entry":
                    current_service['Entry'] = validate_non_negative_integer(value, "Entry", line_number)
                elif key == "Service":
                    current_service['Service'] = value
                elif key == "ServiceType":
                    current_service['ServiceType'] = value
                elif key == "ServiceLocation":
                    current_service['ServiceLocation'] = value
                elif key == "TimeZone":
                    current_service['TimeZone'] = value
                elif key == "Categories":
                    current_service['Categorization']['Categories'] = [category.strip() for category in value.split(",")]
                    if verbose:
                        print("Line {0}: Categories set to {1}".format(line_number, current_service['Categorization']['Categories']))
                elif key == "Forums":
                    current_service['Categorization']['Forums'] = [forum.strip() for forum in value.split(",")]
                    if verbose:
                        print("Line {0}: Forums set to {1}".format(line_number, current_service['Categorization']['Forums']))
                elif line == "--- Start Description Body ---" and in_section['category_list']:
                    # Begin capturing multi-line category Description
                    in_section['description_body'] = True
                    _desc_lines = []
                    continue
                elif line == "--- End Description Body ---" and in_section['category_list']:
                    # Finish the multi-line description
                    in_section['description_body'] = False
                    # Join and store
                    current_category['Description'] = "\n".join(_desc_lines)
                    del _desc_lines
                    continue
                elif in_section['description_body'] and in_section['category_list']:
                    # Accumulate each body‑line
                    _desc_lines.append(line)
                    continue
                elif in_section['category_list']:
                    if key == "Kind":
                        current_category['Kind'] = value
                    elif key == "ID":
                        current_category['ID'] = validate_non_negative_integer(value, "ID", line_number)
                    elif key == "InSub":
                        current_category['InSub'] = validate_non_negative_integer(value, "InSub", line_number)
                    elif key == "Headline":
                        current_category['Headline'] = value
                    elif key == "Description":
                        current_category['Description'] = value
                elif line == "--- Start User List ---":
                    in_section['user_list'] = True
                    if verbose:
                        print("Line {0}: {1} (Starting user list)".format(line_number, line))
                    continue
                elif line == "--- End User List ---":
                    in_section['user_list'] = False
                    if verbose:
                        print("Line {0}: {1} (Ending user list)".format(line_number, line))
                    continue
                elif line == "--- Start User Info ---":
                    in_section['user_info'] = True
                    if verbose:
                        print("Line {0}: {1} (Starting user info)".format(line_number, line))
                    continue
                elif line == "--- End User Info ---":
                    in_section['user_info'] = False
                    user_id = None
                    if verbose:
                        print("Line {0}: {1} (Ending user info)".format(line_number, line))
                    continue
                elif line == "--- Start Message List ---":
                    in_section['message_list'] = True
                    if verbose:
                        print("Line {0}: {1} (Starting message list)".format(line_number, line))
                    continue
                elif line == "--- End Message List ---":
                    in_section['message_list'] = False
                    if verbose:
                        print("Line {0}: {1} (Ending message list)".format(line_number, line))
                    continue
                elif line == "--- Start Message Thread ---":
                    in_section['message_thread'] = True
                    current_thread = {'Title': '', 'Messages': []}
                    post_id = 1
                    if verbose:
                        print("Line {0}: {1} (Starting message thread)".format(line_number, line))
                    continue
                elif line == "--- End Message Thread ---":
                    in_section['message_thread'] = False
                    current_service['MessageThreads'].append(current_thread)
                    current_thread = None
                    if verbose:
                        print("Line {0}: {1} (Ending message thread)".format(line_number, line))
                    continue
                elif line == "--- Start Message Post ---":
                    in_section['message_post'] = True
                    current_message = {}
                    if verbose:
                        print("Line {0}: {1} (Starting message post)".format(line_number, line))
                    continue
                elif line == "--- End Message Post ---":
                    in_section['message_post'] = False
                    if current_message:
                        current_thread['Messages'].append(current_message)
                    current_message = None
                    if verbose:
                        print("Line {0}: {1} (Ending message post)".format(line_number, line))
                    continue
                elif in_section['message_list'] and key == "Interactions":
                    current_service['Interactions'] = [interaction.strip() for interaction in value.split(",")]
                    if verbose:
                        print("Line {0}: Interactions set to {1}".format(line_number, current_service['Interactions']))
                elif in_section['message_list'] and key == "Status":
                    current_service['Status'] = [status.strip() for status in value.split(",")]
                    if verbose:
                        print("Line {0}: Status set to {1}".format(line_number, current_service['Status']))
                elif key == "Info":
                    current_info = []
                    in_section['info_body'] = True
                    if verbose:
                        print("Line {0}: {1} (Starting info body)".format(line_number, line))
                elif in_section['user_list'] and in_section['user_info']:
                    if key == "User":
                        user_id = validate_non_negative_integer(value, "User", line_number)
                        current_service['Users'][user_id] = {'Bio': "", 'Signature': ""}
                        if verbose:
                            print("Line {0}: User ID set to {1}".format(line_number, user_id))
                    elif key == "Name":
                        if user_id is not None:
                            current_service['Users'][user_id]['Name'] = value
                            if verbose:
                                print("Line {0}: Name set to {1}".format(line_number, value))
                    elif key == "Handle":
                        if user_id is not None:
                            current_service['Users'][user_id]['Handle'] = value
                            if verbose:
                                print("Line {0}: Handle set to {1}".format(line_number, value))
                    elif key == "Email":
                        if user_id is not None:
                            current_service['Users'][user_id]['Email'] = value
                            if verbose:
                                print("Line {0}: Email set to {1}".format(line_number, value))
                    elif key == "Phone":
                        if user_id is not None:
                            current_service['Users'][user_id]['Phone'] = value
                            if verbose:
                                print("Line {0}: Phone set to {1}".format(line_number, value))
                    elif key == "Location":
                        if user_id is not None:
                            current_service['Users'][user_id]['Location'] = value
                            if verbose:
                                print("Line {0}: Location set to {1}".format(line_number, value))
                    elif key == "Website":
                        if user_id is not None:
                            current_service['Users'][user_id]['Website'] = value
                            if verbose:
                                print("Line {0}: Website set to {1}".format(line_number, value))
                    elif key == "Avatar":
                        if user_id is not None:
                            current_service['Users'][user_id]['Avatar'] = value
                            if verbose:
                                print("Line {0}: Avatar set to {1}".format(line_number, value))
                    elif key == "Banner":
                        if user_id is not None:
                            current_service['Users'][user_id]['Banner'] = value
                            if verbose:
                                print("Line {0}: Banner set to {1}".format(line_number, value))
                    elif key == "Joined":
                        if user_id is not None:
                            current_service['Users'][user_id]['Joined'] = value
                            if verbose:
                                print("Line {0}: Joined date set to {1}".format(line_number, value))
                    elif key == "Birthday":
                        if user_id is not None:
                            current_service['Users'][user_id]['Birthday'] = value
                            if verbose:
                                print("Line {0}: Birthday set to {1}".format(line_number, value))
                    elif key == "HashTags":
                        if user_id is not None:
                            current_service['Users'][user_id]['HashTags'] = value
                            if verbose:
                                print("Line {0}: HashTags set to {1}".format(line_number, value))
                    elif line == "--- Start Bio Body ---":
                        if user_id is not None:
                            current_bio = []
                            in_section['bio_body'] = True
                            if verbose:
                                print("Line {0}: Starting bio body".format(line_number))
                    elif line == "--- End Bio Body ---":
                        if user_id is not None and current_bio is not None:
                            current_service['Users'][user_id]['Bio'] = "\n".join(current_bio)
                            current_bio = None
                            in_section['bio_body'] = False
                            if verbose:
                                print("Line {0}: Ending bio body".format(line_number))
                    elif in_section['bio_body'] and current_bio is not None:
                        current_bio.append(line)
                        if verbose:
                            print("Line {0}: Adding to bio body: {1}".format(line_number, line))
                    elif line == "--- Start Signature Body ---":
                        if user_id is not None:
                            current_signature = []
                            in_section['signature_body'] = True
                            if verbose:
                                print("Line {0}: Starting signature body".format(line_number))
                    elif line == "--- End Signature Body ---":
                        if user_id is not None and current_signature is not None:
                            current_service['Users'][user_id]['Signature'] = "\n".join(current_signature)
                            current_signature = None
                            in_section['signature_body'] = False
                            if verbose:
                                print("Line {0}: Ending signature body".format(line_number))
                    elif in_section['signature_body'] and current_signature is not None:
                        current_signature.append(line)
                        if verbose:
                            print("Line {0}: Adding to signature body: {1}".format(line_number, line))
                elif in_section['message_list'] and in_section['message_thread']:
                    if key == "Thread":
                        current_thread['Thread'] = validate_non_negative_integer(value, "Thread", line_number)
                        if verbose:
                            print("Line {0}: Thread ID set to {1}".format(line_number, value))
                    elif key == "Category":
                        current_thread['Category'] = [category.strip() for category in value.split(",")]
                        if verbose:
                            print("Line {0}: Category set to {1}".format(line_number, current_thread['Category']))
                    elif key == "Forum":
                        current_thread['Forum'] = [forum.strip() for forum in value.split(",")]
                        if verbose:
                            print("Line {0}: Forum set to {1}".format(line_number, current_thread['Forum']))
                    elif key == "Title":
                        current_thread['Title'] = value
                        if verbose:
                            print("Line {0}: Title set to {1}".format(line_number, value))
                    elif key == "Type":
                        current_thread['Type'] = value
                        if verbose:
                            print("Line {0}: Type set to {1}".format(line_number, value))
                    elif key == "State":
                        current_thread['State'] = value
                        if verbose:
                            print("Line {0}: State set to {1}".format(line_number, value))
                    elif key == "Keywords":
                        current_thread['Keywords'] = value
                        if verbose:
                            print("Line {0}: Keywords set to {1}".format(line_number, value))
                    elif key == "Author":
                        current_message['Author'] = value
                        if verbose:
                            print("Line {0}: Author set to {1}".format(line_number, value))
                    elif key == "Time":
                        current_message['Time'] = value
                        if verbose:
                            print("Line {0}: Time set to {1}".format(line_number, value))
                    elif key == "Date":
                        current_message['Date'] = value
                        if verbose:
                            print("Line {0}: Date set to {1}".format(line_number, value))
                    elif key == "EditTime":
                        current_message['EditTime'] = value
                        if verbose:
                            print("Line {0}: EditTime set to {1}".format(line_number, value))
                    elif key == "EditDate":
                        current_message['EditDate'] = value
                        if verbose:
                            print("Line {0}: EditDate set to {1}".format(line_number, value))
                    elif key == "SubType":
                        current_message['SubType'] = value
                        if verbose:
                            print("Line {0}: SubType set to {1}".format(line_number, value))
                    elif key == "SubTitle":
                        current_message['SubTitle'] = value
                        if verbose:
                            print("Line {0}: SubTitle set to {1}".format(line_number, value))
                    elif key == "Tags":
                        current_message['Tags'] = value
                        if verbose:
                            print("Line {0}: Tags set to {1}".format(line_number, value))
                    elif key == "Post":
                        post_value = validate_non_negative_integer(value, "Post", line_number)
                        current_message['Post'] = post_value
                        if 'post_ids' not in current_thread:
                            current_thread['post_ids'] = []
                        if post_value not in current_thread['post_ids']:
                            current_thread['post_ids'].append(post_value)
                        if verbose:
                            print("Line {0}: Post ID set to {1}".format(line_number, post_value))
                    elif key == "Nested":
                        nested_value = validate_non_negative_integer(value, "Nested", line_number)
                        if nested_value != 0 and nested_value not in current_thread.get('post_ids', []):
                            raise ValueError(
                                "Nested value '{0}' on line {1} does not match any existing Post values in the current thread. Existing Post IDs: {2}".format(
                                    nested_value, line_number, list(current_thread.get('post_ids', [])))
                            )
                        current_message['Nested'] = nested_value
                        if verbose:
                            print("Line {0}: Nested set to {1}".format(line_number, nested_value))
                    elif line == "--- Start Message Body ---":
                        if current_message is not None:
                            current_message['Message'] = []
                            in_section['message_body'] = True
                            if verbose:
                                print("Line {0}: Starting message body".format(line_number))
                    elif line == "--- End Message Body ---":
                        if current_message is not None and 'Message' in current_message:
                            current_message['Message'] = "\n".join(current_message['Message'])
                            in_section['message_body'] = False
                            if verbose:
                                print("Line {0}: Ending message body".format(line_number))
                    elif in_section['message_body'] and current_message is not None and 'Message' in current_message:
                        current_message['Message'].append(line)
                        if verbose:
                            print("Line {0}: Adding to message body: {1}".format(line_number, line))

        if validate_only:
            return True, "", ""

        return services

    except Exception as e:
        if validate_only:
            return False, "Error: {0}".format(str(e)), lines[line_number - 1]
        else:
            raise

def display_services(services):
    for service in services:
        print("Service Entry: {0}".format(service['Entry']))
        print("Service: {0}".format(service['Service']))
        print("Service Type: {0}".format(service['ServiceType']))
        print("Service Location: {0}".format(service['ServiceLocation']))
        print("TimeZone: {0}".format(service['TimeZone']))
        
        if 'Info' in service and service['Info']:
            print("Info: {0}".format(service['Info'].strip().replace("\n", "\n      ")))
        
        print("Interactions: {0}".format(', '.join(service['Interactions'])))
        print("Status: {0}".format(', '.join(service.get('Status', []))))
        
        if 'Categorization' in service and service['Categorization']:
            for category_type, category_levels in service['Categorization'].items():
                print("{0}: {0}".format(category_type, ', '.join(category_levels)))
        
        print("Category List:")
        for category in service['Categories']:
            print("  Type: {0}, Level: {1}".format(category.get('Type', ''), category.get('Level', '')))
            print("  ID: {0}".format(category['ID']))
            print("  In SubID: {0}".format(category['InSub']))
            print("  Headline: {0}".format(category['Headline']))
            print("  Description: {0}".format(category['Description'].strip().replace("\n", "\n    ")))
            print("")
        
        print("User List:")
        for user_id, user_info in service['Users'].items():
            print("  User ID: {0}".format(user_id))
            print("    Name: {0}".format(user_info['Name']))
            print("    Handle: {0}".format(user_info['Handle']))
            print("    Email: {0}".format(user_info.get('Email', '')))
            print("    Phone: {0}".format(user_info.get('Phone', '')))
            print("    Location: {0}".format(user_info.get('Location', '')))
            print("    Website: {0}".format(user_info.get('Website', '')))
            print("    Avatar: {0}".format(user_info.get('Avatar', '')))
            print("    Banner: {0}".format(user_info.get('Banner', '')))
            print("    Joined: {0}".format(user_info.get('Joined', '')))
            print("    Birthday: {0}".format(user_info.get('Birthday', '')))
            print("    HashTags: {0}".format(user_info.get('HashTags', '')))
            print("    Bio:")
            print("      {0}".format(user_info.get('Bio', '').strip().replace("\n", "\n      ")))
            print("    Signature:")
            print("      {0}".format(user_info.get('Signature', '').strip().replace("\n", "\n      ")))
            print("")
        
        print("Message Threads:")
        for idx, thread in enumerate(service['MessageThreads']):
            print("  --- Message Thread {0} ---".format(idx + 1))
            if thread['Title']:
                print("    Title: {0}".format(thread['Title']))
            if 'Category' in thread:
                print("    Category: {0}".format(', '.join(thread['Category'])))
            if 'Forum' in thread:
                print("    Forum: {0}".format(', '.join(thread['Forum'])))
            if 'Type' in thread:
                print("    Type: {0}".format(thread['Type']))
            if 'State' in thread:
                print("    State: {0}".format(thread['State']))
            if 'Keywords' in thread:
                print("    Keywords: {0}".format(thread['Keywords']))
            
            for message in thread['Messages']:
                print("    {0} ({1} on {2}): [{3}] Post ID: {4} Nested: {5}".format(
                    message['Author'], message['Time'], message['Date'],
                    message.get('SubType', 'Post' if message['Post'] == 1 or message['Nested'] == 0 else 'Reply'),
                    message['Post'], message['Nested']))
                
                # Indent each line of the message body but keep it at the same level
                print("      {0}".format(message['Message'].strip().replace("\n", "\n      ")))
                
                if 'Polls' in message and message['Polls']:
                    print("      Polls:")
                    for poll in message['Polls']:
                        print("        Poll {0}:".format(poll.get('Num', '')))
                        print("          Question: {0}".format(poll.get('Question', '')))
                        print("          Answers: {0}".format(", ".join(poll.get('Answers', []))))
                        print("          Results: {0}".format(", ".join(str(r) for r in poll.get('Results', []))))
                        print("          Percentage: {0}".format(", ".join("{:.2f}".format(float(p)) for p in poll.get('Percentage', []))))
                        print("          Votes: {0}".format(poll.get('Votes', '')))
            print("")


def services_to_html(services):
    """
    Render the services list as a styled HTML document string.

    Args:
        services (list of dict): Parsed services data structure.

    Returns:
        str: A complete HTML page.
    """
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
        lines.append('  <h2>Service Entry: {0} — {1}</h2>'.format(
            escape(unicode_type(entry)), escape(unicode_type(name))))

        # Info
        info = svc.get('Info', '').strip()
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
        users = svc.get('Users', {})
        if users:
            lines.append('  <h3>Users</h3>')
            lines.append('  <ul>')
            for uid, u in users.items():
                uname = u.get('Name', '')
                handle = u.get('Handle', '')
                bio = u.get('Bio', '').strip()
                lines.append('    <li><strong>{0}</strong>: {1} ({2})</li>'.format(
                    escape(unicode_type(uid)), escape(unicode_type(uname)), escape(unicode_type(handle))))
                if bio:
                    lines.append('      <blockquote style="white-space: pre-wrap;">{0}</blockquote>'.format(
                        escape(unicode_type(bio))))
            lines.append('  </ul>')

        # Message Threads
        threads = svc.get('MessageThreads', [])
        if threads:
            lines.append('  <h3>Message Threads</h3>')
            for th in threads:
                title = th.get('Title', '')
                lines.append('  <div class="thread-card">')
                lines.append('    <h4>{0}</h4>'.format(
                    escape(unicode_type(title))))

                msgs = th.get('Messages', [])
                if msgs:
                    lines.append('    <ul class="message-list">')
                    for msg in msgs:
                        author = msg.get('Author', '')
                        body = msg.get('Message', '').strip()
                        lines.append('      <li><strong>{0}</strong>: <blockquote style="white-space: pre-wrap;">{1}</blockquote></li>'.format(
                            escape(unicode_type(author)), escape(unicode_type(body))))
                    lines.append('    </ul>')
                lines.append('  </div>')

        lines.append('</div>')

    lines.append('</div>')
    lines.append('</body>')
    lines.append('</html>')

    return '\n'.join(lines)


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


def to_json(services):
    """ Convert the services data structure to JSON """
    return json.dumps(services, indent=2, ensure_ascii=False)

def from_json(json_str):
    """ Convert a JSON string back to the services data structure """
    return json.loads(json_str)

def load_from_json_file(json_filename):
    """ Load the services data structure from a JSON file """
    with open_compressed_file(json_filename) as file:
        return json.load(file)

def save_to_json_file(services, json_filename):
    """ Save the services data structure to a JSON file """
    json_data = json.dumps(services, indent=2, ensure_ascii=False)
    save_compressed_file(json_data, json_filename)


def to_yaml(data):
    """Convert data to a YAML string, if possible."""
    if not HAS_YAML:
        return False
    return yaml.safe_dump(data, default_flow_style=False, allow_unicode=True)

def from_yaml(yaml_str):
    """Convert a YAML string to a Python data structure."""
    if not HAS_YAML:
        return False
    return yaml.safe_load(yaml_str)

def load_from_yaml_file(filename):
    """Load YAML data from a file."""
    if not HAS_YAML:
        return False
    with open_compressed_file(filename, mode='rt', encoding='utf-8') as file:
        return yaml.safe_load(file)

def save_to_yaml_file(data, filename):
    """Save data as YAML to a file."""
    if not HAS_YAML:
        return False
    yaml_data = yaml.safe_dump(data, default_flow_style=False, allow_unicode=True)
    save_compressed_file(yaml_data + "\n", filename)
    return True


def to_marshal(services):
    """Convert the services data structure to a marshaled byte string"""
    return marshal.dumps(services)

def from_marshal(marshal_bytes):
    """Convert a marshaled byte string back to the services data structure"""
    return marshal.loads(marshal_bytes)

def load_from_marshal_file(marshal_filename):
    """Load the services data structure from a marshal file"""
    with open_compressed_file(marshal_filename, mode='rb') as file:
        return marshal.load(file)

def save_to_marshal_file(services, marshal_filename):
    """Save the services data structure to a marshal file"""
    marshal_data = marshal.dumps(services)
    save_compressed_file(marshal_data, marshal_filename, mode='wb')


def to_pickle(services):
    """Convert the services data structure to a pickled byte string"""
    return pickle.dumps(services)

def from_pickle(pickle_bytes):
    """Convert a pickled byte string back to the services data structure"""
    return pickle.loads(pickle_bytes)

def load_from_pickle_file(pickle_filename):
    """Load the services data structure from a pickle file"""
    with open_compressed_file(pickle_filename, mode='rb') as file:
        return pickle.load(file)

def save_to_pickle_file(services, pickle_filename):
    """Save the services data structure to a pickle file"""
    pickle_data = pickle.dumps(services)
    save_compressed_file(pickle_data, pickle_filename, mode='wb')


def to_array(data):
    """Convert data to a string (like a Python literal)."""
    return str(data)

def from_array(data_str):
    """Convert a string back to data (safe evaluation)."""
    return ast.literal_eval(data_str)

def load_from_array_file(array_filename):
    """ Load the data structure from a raw array-format file """
    with open_compressed_file(array_filename, mode='rt', encoding='utf-8') as file:
        return ast.literal_eval(file.read())

def save_to_array_file(data, array_filename):
    """ Save the data structure to a raw array-format file """
    data_str = str(data)
    save_compressed_file(data_str + "\n", array_filename)


def services_to_string(services, line_ending='lf'):
    """
    Serialize services into the archive text format, preserving all markers and multi-line bodies.
    Supports both LF and CRLF line endings.
    """
    output = []

    for service in services:
        # Service wrapper
        output.append('--- Start Archive Service ---')
        output.append('Entry: {0}'.format(service.get('Entry', '')))
        output.append('Service: {0}'.format(service.get('Service', '')))
        output.append('ServiceType: {0}'.format(service.get('ServiceType', '')))
        output.append('ServiceLocation: {0}'.format(service.get('ServiceLocation', '')))
        output.append('TimeZone: {0}'.format(service.get('TimeZone', 'UTC')))

        # Info section
        if 'Info' in service:
            output.append('Info:')
            output.append('--- Start Info Body ---')
            for line in service['Info'].splitlines():
                output.append(line)
            output.append('--- End Info Body ---')
            output.append('')

        # User list
        users = service.get('Users', {})
        if users:
            output.append('--- Start User List ---')
            for uid, user in users.items():
                output.append('--- Start User Info ---')
                output.append('User: {0}'.format(uid))
                output.append('Name: {0}'.format(user.get('Name', '')))
                output.append('Handle: {0}'.format(user.get('Handle', '')))
                output.append('Email: {0}'.format(user.get('Email', '')))
                output.append('Phone: {0}'.format(user.get('Phone', '')))
                output.append('Location: {0}'.format(user.get('Location', '')))
                output.append('Website: {0}'.format(user.get('Website', '')))
                output.append('Avatar: {0}'.format(user.get('Avatar', '')))
                output.append('Banner: {0}'.format(user.get('Banner', '')))
                output.append('Joined: {0}'.format(user.get('Joined', '')))
                output.append('Birthday: {0}'.format(user.get('Birthday', '')))
                output.append('HashTags: {0}'.format(user.get('HashTags', '')))
                # Bio body
                output.append('Bio:')
                output.append('--- Start Bio Body ---')
                for line in user.get('Bio', '').splitlines():
                    output.append(line)
                output.append('--- End Bio Body ---')
                # Signature body
                output.append('Signature:')
                output.append('--- Start Signature Body ---')
                for line in user.get('Signature', '').splitlines():
                    output.append(line)
                output.append('--- End Signature Body ---')
                output.append('--- End User Info ---')
                output.append('')
            output.append('--- End User List ---')
            output.append('')

        # Categorization list
        if service.get('Categorization'):
            cat = service['Categorization']
            output.append('--- Start Categorization List ---')
            output.append('Categories: {0}'.format(', '.join(cat.get('Categories', []))))
            output.append('Forums: {0}'.format(', '.join(cat.get('Forums', []))))
            output.append('--- End Categorization List ---')
            output.append('')

        # Detailed categories
        for cat in service.get('Categories', []):
            output.append('--- Start Category List ---')
            output.append('Kind: {0}, {1}'.format(cat.get('Type', ''), cat.get('Level', '')))
            output.append('ID: {0}'.format(cat.get('ID', '')))
            output.append('InSub: {0}'.format(cat.get('InSub', '')))
            output.append('Headline: {0}'.format(cat.get('Headline', '')))
            output.append('Description:')
            output.append('--- Start Description Body ---')
            for line in cat.get('Description', '').splitlines():
                output.append(line)
            output.append('--- End Description Body ---')
            output.append('--- End Category List ---')
            output.append('')

        # Message list
        threads = service.get('MessageThreads', [])
        if threads:
            output.append('--- Start Message List ---')
            if service.get('Interactions'):
                output.append('Interactions: {0}'.format(', '.join(service['Interactions'])))
            if service.get('Status'):
                output.append('Status: {0}'.format(', '.join(service['Status'])))
            output.append('')

            for thread in threads:
                output.append('--- Start Message Thread ---')
                output.append('Thread: {0}'.format(thread.get('Thread', '')))
                output.append('Title: {0}'.format(thread.get('Title', '')))
                output.append('Type: {0}'.format(thread.get('Type', '')))
                output.append('State: {0}'.format(thread.get('State', '')))
                output.append('Keywords: {0}'.format(thread.get('Keywords', '')))
                output.append('Category: {0}'.format(', '.join(thread.get('Category', []))))
                output.append('Forum: {0}'.format(', '.join(thread.get('Forum', []))))
                output.append('')

                for msg in thread.get('Messages', []):
                    output.append('--- Start Message Post ---')
                    output.append('Author: {0}'.format(msg.get('Author', '')))
                    output.append('Time: {0}'.format(msg.get('Time', '')))
                    output.append('Date: {0}'.format(msg.get('Date', '')))
                    output.append('EditTime: {0}'.format(msg.get('EditTime', '')))
                    output.append('EditDate: {0}'.format(msg.get('EditDate', '')))
                    output.append('SubType: {0}'.format(msg.get('SubType', '')))
                    output.append('SubTitle: {0}'.format(msg.get('SubTitle', '')))
                    output.append('Tags: {0}'.format(msg.get('Tags', '')))
                    output.append('Post: {0}'.format(msg.get('Post', '')))
                    output.append('Nested: {0}'.format(msg.get('Nested', '')))
                    # Message body
                    output.append('Message:')
                    output.append('--- Start Message Body ---')
                    for line in msg.get('Message', '').splitlines():
                        output.append(line)
                    output.append('--- End Message Body ---')

                    # Polls
                    if 'Polls' in msg and msg['Polls']:
                        output.append('Polls:')
                        output.append('--- Start Poll List ---')
                        for poll in msg['Polls']:
                            output.append('--- Start Poll Body ---')
                            output.append('Num: {0}'.format(poll.get('Num', '')))
                            output.append('Question: {0}'.format(poll.get('Question', '')))
                            output.append('Answers: {0}'.format(', '.join(poll.get('Answers', []))))
                            output.append('Results: {0}'.format(', '.join(str(r) for r in poll.get('Results', []))))
                            output.append('Percentage: {0}'.format(', '.join('{:.1f}'.format(float(p)) for p in poll.get('Percentage', []))))
                            output.append('Votes: {0}'.format(poll.get('Votes', '')))
                            output.append('--- End Poll Body ---')
                        output.append('--- End Poll List ---')
                    output.append('--- End Message Post ---')
                    output.append('')

                output.append('--- End Message Thread ---')
                output.append('')

            output.append('--- End Message List ---')
            output.append('')

        # Close service
        output.append('--- End Archive Service ---')
        output.append('')

    data = '\n'.join(output)
    if line_ending.lower() == 'crlf':
        data = data.replace('\n', '\r\n')
    return data


def save_services_to_file(services, filename, line_ending='lf'):
    """
    Save services to a file, inferring compression by extension (Python 2/3 compatible).
    """
    data = services_to_string(services, line_ending)
    save_compressed_file(data, filename)


def init_empty_service(entry, service_name, service_type, service_location, time_zone="UTC", info=''):
    """ Initialize an empty service structure """
    return {
        'Entry': entry,
        'Service': service_name,
        'ServiceType': service_type,
        'ServiceLocation': service_location,
        'TimeZone': time_zone,
        'Users': {},
        'MessageThreads': [],
        'Categories': [],
        'Interactions': [],
        'Categorization': {},
        'Info': info,
    }

def add_user(service, user_id, name, handle, emailaddr, phonenum, location, website, avatar, banner, joined, birthday, hashtags, bio, signature):
    """ Add a user to the service """
    service['Users'][user_id] = {
        'Name': name,
        'Handle': handle,
        'Email': emailaddr,
        'Phone': phonenum,
        'Location': location,
        'Website': website,
        'Avatar': website,
        'Banner': website,
        'Joined': joined,
        'Birthday': birthday,
        'HashTags': hashtags,
        'Bio': bio,
        'Signature': signature
    }

def add_category(service, kind, category_type, category_level, category_id, insub, headline, description):
    category = {
        'Kind': "{0}, {1}".format(kind, category_level),
        'Type': category_type,
        'Level': category_level,
        'ID': category_id,
        'InSub': insub,
        'Headline': headline,
        'Description': description
    }
    service['Categories'].append(category)
    if category_type not in service['Categorization']:
        service['Categorization'][category_type] = []
    if category_level not in service['Categorization'][category_type]:
        service['Categorization'][category_type].append(category_level)
    if insub != 0:
        if not any(cat['ID'] == insub for cat in service['Categories']):
            raise ValueError("InSub value '{0}' does not match any existing ID in service.".format(insub))

def add_message_thread(service, thread_id, title, category, forum, thread_type, thread_state, thread_keywords):
    """ Add a message thread to the service """
    thread = {
        'Thread': thread_id,
        'Title': title,
        'Category': category.split(',') if category else [],
        'Forum': forum.split(',') if forum else [],
        'Type': thread_type,
        'State': thread_state,
        'Keywords': thread_keywords,
        'Messages': []
    }
    service['MessageThreads'].append(thread)

def add_message_post(service, thread_id, author, time, date, edittime, editdate, subtype, tags, post_id, nested, message):
    thread = next((t for t in service['MessageThreads'] if t['Thread'] == thread_id), None)
    if thread is not None:
        new_post = {
            'Author': author,
            'Time': time,
            'Date': date,
            'EditTime': edittime,
            'EditDate': editdate,
            'SubType': subtype,
            'SubTitle': subtitle,
            'Tags': tags,
            'Post': post_id,
            'Nested': nested,
            'Message': message
        }
        thread['Messages'].append(new_post)
    else:
        raise ValueError("Thread ID {0} not found in service.".format(thread_id))

def add_poll(service, thread_id, post_id, poll_num, question, answers, results, percentages, votes):
    thread = next((t for t in service['MessageThreads'] if t['Thread'] == thread_id), None)
    if thread is not None:
        message = next((m for m in thread['Messages'] if m['Post'] == post_id), None)
        if message is not None:
            if 'Polls' not in message:
                message['Polls'] = []
            new_poll = {
                'Num': poll_num,
                'Question': question,
                'Answers': answers,
                'Results': results,
                'Percentage': percentages,
                'Votes': votes
            }
            message['Polls'].append(new_poll)
        else:
            raise ValueError("Post ID {0} not found in thread {1}.".format(post_id, thread_id))
    else:
        raise ValueError("Thread ID {0} not found in service.".format(thread_id))

def remove_user(service, user_id):
    if user_id in service['Users']:
        del service['Users'][user_id]
    else:
        raise ValueError("User ID {0} not found in service.".format(user_id))

def remove_category(service, category_id):
    category = next((c for c in service['Categories'] if c['ID'] == category_id), None)
    if category:
        service['Categories'].remove(category)
    else:
        raise ValueError("Category ID {0} not found in service.".format(category_id))

def remove_message_thread(service, thread_id):
    thread = next((t for t in service['MessageThreads'] if t['Thread'] == thread_id), None)
    if thread:
        service['MessageThreads'].remove(thread)
    else:
        raise ValueError("Thread ID {0} not found in service.".format(thread_id))

def remove_message_post(service, thread_id, post_id):
    thread = next((t for t in service['MessageThreads'] if t['Thread'] == thread_id), None)
    if thread is not None:
        message = next((m for m in thread['Messages'] if m['Post'] == post_id), None)
        if message is not None:
            thread['Messages'].remove(message)
        else:
            raise ValueError("Post ID {0} not found in thread {1}.".format(post_id, thread_id))
    else:
        raise ValueError("Thread ID {0} not found in service.".format(thread_id))

def add_service(services, entry, service_name, service_type, service_location, time_zone="UTC", info=None):
    new_service = {
        'Entry': entry,
        'Service': service_name,
        'ServiceType': service_type,
        'ServiceLocation': service_location,
        'TimeZone': time_zone,
        'Info': info if info else '',
        'Interactions': [],
        'Status': [],
        'Categorization': {'Categories': [], 'Forums': []},
        'Categories': [],
        'Users': {},
        'MessageThreads': []
    }
    services.append(new_service)
    return new_service  # Return the newly created service

def remove_service(services, entry):
    service = next((s for s in services if s['Entry'] == entry), None)
    if service:
        services.remove(service)
    else:
        raise ValueError("Service entry {0} not found.".format(entry))


def download_file_from_ftp_file(url):
    urlparts = urlparse(url)
    file_name = os.path.basename(urlparts.path)
    file_dir = os.path.dirname(urlparts.path)
    if(urlparts.username is not None):
        ftp_username = urlparts.username
    else:
        ftp_username = "anonymous"
    if(urlparts.password is not None):
        ftp_password = urlparts.password
    elif(urlparts.password is None and urlparts.username == "anonymous"):
        ftp_password = "anonymous"
    else:
        ftp_password = ""
    if(urlparts.scheme == "ftp"):
        ftp = FTP()
    elif(urlparts.scheme == "ftps" and ftpssl):
        ftp = FTP_TLS()
    else:
        return False
    if(urlparts.scheme == "sftp"):
        if(__use_pysftp__):
            return download_file_from_pysftp_file(url)
        else:
            return download_file_from_sftp_file(url)
    elif(urlparts.scheme == "http" or urlparts.scheme == "https"):
        return download_file_from_http_file(url)
    ftp_port = urlparts.port
    if(urlparts.port is None):
        ftp_port = 21
    try:
        ftp.connect(urlparts.hostname, ftp_port)
    except socket.gaierror:
        log.info("Error With URL "+url)
        return False
    except socket.timeout:
        log.info("Error With URL "+url)
        return False
    ftp.login(urlparts.username, urlparts.password)
    if(urlparts.scheme == "ftps"):
        ftp.prot_p()
    ftpfile = BytesIO()
    ftp.retrbinary("RETR "+urlparts.path, ftpfile.write)
    #ftp.storbinary("STOR "+urlparts.path, ftpfile.write);
    ftp.close()
    ftpfile.seek(0, 0)
    return ftpfile


def download_file_from_ftp_string(url):
    ftpfile = download_file_from_ftp_file(url)
    return ftpfile.read()


def upload_file_to_ftp_file(ftpfile, url):
    urlparts = urlparse(url)
    file_name = os.path.basename(urlparts.path)
    file_dir = os.path.dirname(urlparts.path)
    if(urlparts.username is not None):
        ftp_username = urlparts.username
    else:
        ftp_username = "anonymous"
    if(urlparts.password is not None):
        ftp_password = urlparts.password
    elif(urlparts.password is None and urlparts.username == "anonymous"):
        ftp_password = "anonymous"
    else:
        ftp_password = ""
    if(urlparts.scheme == "ftp"):
        ftp = FTP()
    elif(urlparts.scheme == "ftps" and ftpssl):
        ftp = FTP_TLS()
    else:
        return False
    if(urlparts.scheme == "sftp"):
        if(__use_pysftp__):
            return upload_file_to_pysftp_file(url)
        else:
            return upload_file_to_sftp_file(url)
    elif(urlparts.scheme == "http" or urlparts.scheme == "https"):
        return False
    ftp_port = urlparts.port
    if(urlparts.port is None):
        ftp_port = 21
    try:
        ftp.connect(urlparts.hostname, ftp_port)
    except socket.gaierror:
        log.info("Error With URL "+url)
        return False
    except socket.timeout:
        log.info("Error With URL "+url)
        return False
    ftp.login(urlparts.username, urlparts.password)
    if(urlparts.scheme == "ftps"):
        ftp.prot_p()
    ftp.storbinary("STOR "+urlparts.path, ftpfile)
    ftp.close()
    ftpfile.seek(0, 0)
    return ftpfile


def upload_file_to_ftp_string(ftpstring, url):
    ftpfileo = BytesIO(ftpstring)
    ftpfile = upload_file_to_ftp_file(ftpfileo, url)
    ftpfileo.close()
    return ftpfile


class RawIteratorWrapper:
    def __init__(self, iterator):
        self.iterator = iterator
        self.buffer = b""
        self._iterator_exhausted = False

    def read(self, size=-1):
        if self._iterator_exhausted:
            return b''
        while size < 0 or len(self.buffer) < size:
            try:
                chunk = next(self.iterator)
                self.buffer += chunk
            except StopIteration:
                self._iterator_exhausted = True
                break
        if size < 0:
            size = len(self.buffer)
        result, self.buffer = self.buffer[:size], self.buffer[size:]
        return result


def download_file_from_http_file(url, headers=None, usehttp=__use_http_lib__):
    if headers is None:
        headers = {}
    urlparts = urlparse(url)
    username = urlparts.username
    password = urlparts.password

    # Rebuild URL without username and password
    netloc = urlparts.hostname or ''
    if urlparts.port:
        netloc += ':' + str(urlparts.port)
    rebuilt_url = urlunparse((urlparts.scheme, netloc, urlparts.path,
                              urlparts.params, urlparts.query, urlparts.fragment))

    # Handle SFTP/FTP
    if urlparts.scheme == "sftp":
        if __use_pysftp__:
            return download_file_from_pysftp_file(url)
        else:
            return download_file_from_sftp_file(url)
    elif urlparts.scheme == "ftp" or urlparts.scheme == "ftps":
        return download_file_from_ftp_file(url)

    # Create a temporary file object
    httpfile = BytesIO()

    # 1) Requests branch
    if usehttp == 'requests' and haverequests:
        if username and password:
            response = requests.get(
                rebuilt_url, headers=headers, auth=(username, password), stream=True
            )
        else:
            response = requests.get(rebuilt_url, headers=headers, stream=True)
        response.raw.decode_content = True
        shutil.copyfileobj(response.raw, httpfile)

    # 2) HTTPX branch
    elif usehttp == 'httpx' and havehttpx:
        with httpx.Client(follow_redirects=True) as client:
            if username and password:
                response = client.get(
                    rebuilt_url, headers=headers, auth=(username, password)
                )
            else:
                response = client.get(rebuilt_url, headers=headers)
            raw_wrapper = RawIteratorWrapper(response.iter_bytes())
            shutil.copyfileobj(raw_wrapper, httpfile)

    # 3) Mechanize branch
    elif usehttp == 'mechanize' and havemechanize:
        # Create a mechanize browser
        br = mechanize.Browser()
        # Optional: configure mechanize (disable robots.txt, handle redirects, etc.)
        br.set_handle_robots(False)
        # If you need custom headers, add them as a list of (header_name, header_value)
        if headers:
            br.addheaders = list(headers.items())

        # If you need to handle basic auth:
        if username and password:
            # Mechanize has its own password manager; this is one way to do it:
            br.add_password(rebuilt_url, username, password)

        # Open the URL and copy the response to httpfile
        response = br.open(rebuilt_url)
        shutil.copyfileobj(response, httpfile)

    # 4) Fallback to urllib
    else:
        request = Request(rebuilt_url, headers=headers)
        if username and password:
            password_mgr = HTTPPasswordMgrWithDefaultRealm()
            password_mgr.add_password(None, rebuilt_url, username, password)
            auth_handler = HTTPBasicAuthHandler(password_mgr)
            opener = build_opener(auth_handler)
        else:
            opener = build_opener()
        response = opener.open(request)
        shutil.copyfileobj(response, httpfile)

    # Reset file pointer to the start before returning
    httpfile.seek(0, 0)
    return httpfile


def download_file_from_http_string(url, headers=geturls_headers_upcean_python_alt, usehttp=__use_http_lib__):
    httpfile = download_file_from_http_file(url, headers, usehttp)
    return httpfile.read()


if(haveparamiko):
    def download_file_from_sftp_file(url):
        urlparts = urlparse(url)
        file_name = os.path.basename(urlparts.path)
        file_dir = os.path.dirname(urlparts.path)
        sftp_port = urlparts.port
        if(urlparts.port is None):
            sftp_port = 22
        else:
            sftp_port = urlparts.port
        if(urlparts.username is not None):
            sftp_username = urlparts.username
        else:
            sftp_username = "anonymous"
        if(urlparts.password is not None):
            sftp_password = urlparts.password
        elif(urlparts.password is None and urlparts.username == "anonymous"):
            sftp_password = "anonymous"
        else:
            sftp_password = ""
        if(urlparts.scheme == "ftp"):
            return download_file_from_ftp_file(url)
        elif(urlparts.scheme == "http" or urlparts.scheme == "https"):
            return download_file_from_http_file(url)
        if(urlparts.scheme != "sftp"):
            return False
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(urlparts.hostname, port=sftp_port,
                        username=urlparts.username, password=urlparts.password)
        except paramiko.ssh_exception.SSHException:
            return False
        except socket.gaierror:
            log.info("Error With URL "+url)
            return False
        except socket.timeout:
            log.info("Error With URL "+url)
            return False
        sftp = ssh.open_sftp()
        sftpfile = BytesIO()
        sftp.getfo(urlparts.path, sftpfile)
        sftp.close()
        ssh.close()
        sftpfile.seek(0, 0)
        return sftpfile
else:
    def download_file_from_sftp_file(url):
        return False

if(haveparamiko):
    def download_file_from_sftp_string(url):
        sftpfile = download_file_from_sftp_file(url)
        return sftpfile.read()
else:
    def download_file_from_sftp_string(url):
        return False

if(haveparamiko):
    def upload_file_to_sftp_file(sftpfile, url):
        urlparts = urlparse(url)
        file_name = os.path.basename(urlparts.path)
        file_dir = os.path.dirname(urlparts.path)
        sftp_port = urlparts.port
        if(urlparts.port is None):
            sftp_port = 22
        else:
            sftp_port = urlparts.port
        if(urlparts.username is not None):
            sftp_username = urlparts.username
        else:
            sftp_username = "anonymous"
        if(urlparts.password is not None):
            sftp_password = urlparts.password
        elif(urlparts.password is None and urlparts.username == "anonymous"):
            sftp_password = "anonymous"
        else:
            sftp_password = ""
        if(urlparts.scheme == "ftp"):
            return upload_file_to_ftp_file(url)
        elif(urlparts.scheme == "http" or urlparts.scheme == "https"):
            return False
        if(urlparts.scheme != "sftp"):
            return False
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(urlparts.hostname, port=sftp_port,
                        username=urlparts.username, password=urlparts.password)
        except paramiko.ssh_exception.SSHException:
            return False
        except socket.gaierror:
            log.info("Error With URL "+url)
            return False
        except socket.timeout:
            log.info("Error With URL "+url)
            return False
        sftp = ssh.open_sftp()
        sftp.putfo(sftpfile, urlparts.path)
        sftp.close()
        ssh.close()
        sftpfile.seek(0, 0)
        return sftpfile
else:
    def upload_file_to_sftp_file(sftpfile, url):
        return False

if(haveparamiko):
    def upload_file_to_sftp_string(sftpstring, url):
        sftpfileo = BytesIO(sftpstring)
        sftpfile = upload_file_to_sftp_files(ftpfileo, url)
        sftpfileo.close()
        return sftpfile
else:
    def upload_file_to_sftp_string(url):
        return False

if(havepysftp):
    def download_file_from_pysftp_file(url):
        urlparts = urlparse(url)
        file_name = os.path.basename(urlparts.path)
        file_dir = os.path.dirname(urlparts.path)
        sftp_port = urlparts.port
        if(urlparts.port is None):
            sftp_port = 22
        else:
            sftp_port = urlparts.port
        if(urlparts.username is not None):
            sftp_username = urlparts.username
        else:
            sftp_username = "anonymous"
        if(urlparts.password is not None):
            sftp_password = urlparts.password
        elif(urlparts.password is None and urlparts.username == "anonymous"):
            sftp_password = "anonymous"
        else:
            sftp_password = ""
        if(urlparts.scheme == "ftp"):
            return download_file_from_ftp_file(url)
        elif(urlparts.scheme == "http" or urlparts.scheme == "https"):
            return download_file_from_http_file(url)
        if(urlparts.scheme != "sftp"):
            return False
        try:
            pysftp.Connection(urlparts.hostname, port=sftp_port,
                              username=urlparts.username, password=urlparts.password)
        except paramiko.ssh_exception.SSHException:
            return False
        except socket.gaierror:
            log.info("Error With URL "+url)
            return False
        except socket.timeout:
            log.info("Error With URL "+url)
            return False
        sftp = ssh.open_sftp()
        sftpfile = BytesIO()
        sftp.getfo(urlparts.path, sftpfile)
        sftp.close()
        ssh.close()
        sftpfile.seek(0, 0)
        return sftpfile
else:
    def download_file_from_pysftp_file(url):
        return False

if(havepysftp):
    def download_file_from_pysftp_string(url):
        sftpfile = download_file_from_pysftp_file(url)
        return sftpfile.read()
else:
    def download_file_from_pyftp_string(url):
        return False

if(havepysftp):
    def upload_file_to_pysftp_file(sftpfile, url):
        urlparts = urlparse(url)
        file_name = os.path.basename(urlparts.path)
        file_dir = os.path.dirname(urlparts.path)
        sftp_port = urlparts.port
        if(urlparts.port is None):
            sftp_port = 22
        else:
            sftp_port = urlparts.port
        if(urlparts.username is not None):
            sftp_username = urlparts.username
        else:
            sftp_username = "anonymous"
        if(urlparts.password is not None):
            sftp_password = urlparts.password
        elif(urlparts.password is None and urlparts.username == "anonymous"):
            sftp_password = "anonymous"
        else:
            sftp_password = ""
        if(urlparts.scheme == "ftp"):
            return upload_file_to_ftp_file(url)
        elif(urlparts.scheme == "http" or urlparts.scheme == "https"):
            return False
        if(urlparts.scheme != "sftp"):
            return False
        try:
            pysftp.Connection(urlparts.hostname, port=sftp_port,
                              username=urlparts.username, password=urlparts.password)
        except paramiko.ssh_exception.SSHException:
            return False
        except socket.gaierror:
            log.info("Error With URL "+url)
            return False
        except socket.timeout:
            log.info("Error With URL "+url)
            return False
        sftp = ssh.open_sftp()
        sftp.putfo(sftpfile, urlparts.path)
        sftp.close()
        ssh.close()
        sftpfile.seek(0, 0)
        return sftpfile
else:
    def upload_file_to_pysftp_file(sftpfile, url):
        return False

if(havepysftp):
    def upload_file_to_pysftp_string(sftpstring, url):
        sftpfileo = BytesIO(sftpstring)
        sftpfile = upload_file_to_pysftp_files(ftpfileo, url)
        sftpfileo.close()
        return sftpfile
else:
    def upload_file_to_pysftp_string(url):
        return False


def download_file_from_internet_file(url, headers=geturls_headers_upcean_python_alt, usehttp=__use_http_lib__):
    urlparts = urlparse(url)
    if(urlparts.scheme == "http" or urlparts.scheme == "https"):
        return download_file_from_http_file(url, headers, usehttp)
    elif(urlparts.scheme == "ftp" or urlparts.scheme == "ftps"):
        return download_file_from_ftp_file(url)
    elif(urlparts.scheme == "sftp"):
        if(__use_pysftp__ and havepysftp):
            return download_file_from_pysftp_file(url)
        else:
            return download_file_from_sftp_file(url)
    else:
        return False
    return False


def download_file_from_internet_string(url, headers=geturls_headers_upcean_python_alt):
    urlparts = urlparse(url)
    if(urlparts.scheme == "http" or urlparts.scheme == "https"):
        return download_file_from_http_string(url, headers)
    elif(urlparts.scheme == "ftp" or urlparts.scheme == "ftps"):
        return download_file_from_ftp_string(url)
    elif(urlparts.scheme == "sftp"):
        if(__use_pysftp__ and havepysftp):
            return download_file_from_pysftp_string(url)
        else:
            return download_file_from_sftp_string(url)
    else:
        return False
    return False


def upload_file_to_internet_file(ifp, url):
    urlparts = urlparse(url)
    if(urlparts.scheme == "http" or urlparts.scheme == "https"):
        return False
    elif(urlparts.scheme == "ftp" or urlparts.scheme == "ftps"):
        return upload_file_to_ftp_file(ifp, url)
    elif(urlparts.scheme == "sftp"):
        if(__use_pysftp__ and havepysftp):
            return upload_file_to_pysftp_file(ifp, url)
        else:
            return upload_file_to_sftp_file(ifp, url)
    else:
        return False
    return False


def upload_file_to_internet_string(ifp, url):
    urlparts = urlparse(url)
    if(urlparts.scheme == "http" or urlparts.scheme == "https"):
        return False
    elif(urlparts.scheme == "ftp" or urlparts.scheme == "ftps"):
        return upload_file_to_ftp_string(ifp, url)
    elif(urlparts.scheme == "sftp"):
        if(__use_pysftp__ and havepysftp):
            return upload_file_to_pysftp_string(ifp, url)
        else:
            return upload_file_to_sftp_string(ifp, url)
    else:
        return False
    return False

