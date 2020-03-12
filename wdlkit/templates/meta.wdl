{% if meta %}meta {{ "{" }}{% for key, val in meta.items() %}
{{ key | indent(2, True) }}: {{ val | indent(2, False) }}{% endfor %}
}{% endif %}