import subprocess
import shutil
import tempfile
import os

from django.conf import settings
from django.template.loader import render_to_string

from logging import getLogger
log = getLogger(__name__)

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
    
from django.conf import settings

class ConvertError(Exception):
    pass

def convert_file_to_pdf(fileobj, outfilename=None,
                        cmd_args=settings.WKHTML_DEFAULT_ARGS):
    """Convert a file to pdf.

    Returns a temporary filename outfilename is not provided.
    The input is better to be text/html"""
    log.debug("fileobj=%s" % fileobj)
    log.debug("wkhtml args=%s" % cmd_args)
    log.debug("outfile=%s" % outfilename)
    if not outfilename:
        outfile, outfilename = tempfile.mkstemp(suffix='.pdf')
        log.debug("temp_pdf_file=%s" % outfilename)
        os.close(outfile)
    else:
        outdirname = os.path.dirname(outfilename)
        log.debug("out_dir=%s" % outdirname)
        if not os.path.exists(outdirname):
            os.makedirs(outdirname)
    tempfileobj, tempfilename = tempfile.mkstemp(suffix='.html')
    log.debug("temp_html_file=%s" % tempfilename)
    tempfileobj = os.fdopen(tempfileobj, 'wb')
    log.debug("copying temp html")
    shutil.copyfileobj(fileobj, tempfileobj)
    tempfileobj.close()
    cmd_args = cmd_args or []
    cmdline = [settings.WKHTML_PATH] + cmd_args + [tempfilename, outfilename]
    process = subprocess.Popen(cmdline,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    log.debug("running %s (%s)" % (' '.join(cmdline),process))
    stdout, stderr = process.communicate()
    os.remove(tempfilename)
    if process.returncode > 0:
        raise ConvertError(stderr)
    return outfilename

def convert_string_to_pdf(string, *args, **kwargs):
    """Same as convert_file_to_pdf, but takes a string as input"""
    if isinstance(string, unicode):
        string = string.encode('utf-8')
    log.debug("string len=%d" % len(string))
    f = StringIO(string)
    return convert_file_to_pdf(f, *args, **kwargs)

def render_to_pdf(template_name, context=None, outfilename=None, *args, **kwargs):
    log.debug("template_name=%s" % template_name)
    log.debug("context=%s" % context)
    log.debug("outfile=%s" % outfilename)
    context = context or {}
    return convert_string_to_pdf(render_to_string(template_name, context),
                                 outfilename, *args, **kwargs)
