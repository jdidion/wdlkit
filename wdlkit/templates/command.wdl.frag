command <<<
{{ value | trim("\n") | replace("\t", "  ") | dedent() | trim() }}
>>>