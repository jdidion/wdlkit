version 1.0{% if imports %}
{{ imports }}{% endif %}{% if structs %}

{{ structs}}{% endif %}{% if workflow %}

{{ workflow }}{% endif %}{% if tasks %}{% for task in tasks %}

{{ task }}{% endfor %}{% endif %}