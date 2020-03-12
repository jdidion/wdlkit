command <<<
{{ command | trim("\n") | replace("\t", "  ") | dedent() | trim() }}
>>>