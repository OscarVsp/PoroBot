import traceback

def tracebackEx(ex):
    if type(ex) == str:
        return "No valid traceback."
    ex_traceback = ex.__traceback__
    if ex_traceback is None:
        ex_traceback = ex.__traceback__
    tb_lines = [ line.rstrip('\n') for line in
        traceback.format_exception(ex.__class__, ex, ex_traceback)]
    return ''.join(tb_lines)
