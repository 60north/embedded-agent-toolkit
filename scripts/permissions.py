"""Preserve config text while adding only the shared memory directory as writable."""
import json
import re
import tomllib


def codex_memory(text, memory):
    data=tomllib.loads(text)
    if 'permissions' in data or 'default_permissions' in data:
        raise ValueError('Existing Codex permission profiles require a reviewed memory-path rule; legacy writable_roots cannot be mixed with them')
    section=data.get('sandbox_workspace_write',{})
    roots=section.get('writable_roots',[])
    if not isinstance(roots,list) or not all(isinstance(v,str) for v in roots):raise ValueError('Invalid Codex writable_roots')
    if memory in roots:return text
    value=json.dumps([*roots,memory],ensure_ascii=False)
    # Handle the normal table form, conservatively refusing ambiguous TOML edits.
    table=re.search(r'(?m)^\[sandbox_workspace_write\][ \t]*(?:#.*)?$',text)
    if table:
        start=table.end();following=re.search(r'(?m)^\[',text[start:]);end=start+following.start() if following else len(text)
        body=text[start:end]
        if 'writable_roots' in section:
            match=re.search(r'(?ms)^([ \t]*writable_roots[ \t]*=[ \t]*)(\[.*?\])',body)
            if not match or tomllib.loads('x='+match.group(2)).get('x')!=roots:
                raise ValueError('Cannot safely edit this writable_roots syntax')
            body=body[:match.start(2)]+value+body[match.end(2):]
        else:body='\nwritable_roots = '+value+body
        result=text[:start]+body+text[end:]
    elif 'sandbox_workspace_write' in data:
        raise ValueError('Use table form for sandbox_workspace_write before installation')
    else:result=text.rstrip()+'\n\n[sandbox_workspace_write]\nwritable_roots = '+value+'\n'
    parsed=tomllib.loads(result)
    expected=dict(data);expected['sandbox_workspace_write']=dict(section,writable_roots=[*roots,memory])
    if parsed!=expected:raise ValueError('Unexpected Codex configuration change')
    return result


def claude_memory(text,memory):
    data=json.loads(text) if text.strip() else {}
    if not isinstance(data,dict):raise ValueError('Claude settings must be a JSON object')
    permissions=data.setdefault('permissions',{})
    dirs=permissions.setdefault('additionalDirectories',[])
    if not isinstance(dirs,list):raise ValueError('Invalid Claude additionalDirectories')
    if memory in dirs:return text
    dirs.append(memory)
    return json.dumps(data,indent=2,ensure_ascii=False)+'\n'
