version 1.0{% if imports %}
{{ imports }}{% endif %}{% if structs %}{% for struct in structs %}

{{ struct }}{% endfor %}{% endif %}{% if workflow %}

{{ workflow }}{% endif %}{% if tasks %}{% for task in tasks %}

{{ task }}{% endfor %}{% endif %}