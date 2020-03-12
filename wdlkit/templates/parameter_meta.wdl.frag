{% if value %}parameter_meta {{ "{" }}{% for key, val in value.items() %}
{{ key | indent(2, True) }}: {{ val | indent(2, False) }}{% endfor %}
}{% endif %}