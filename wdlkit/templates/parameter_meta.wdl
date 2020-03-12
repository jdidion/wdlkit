{% if parameter_meta %}parameter_meta {{ "{" }}{% for key, val in parameter_meta.items() %}
{{ key | indent(2, True) }}: {{ val | indent(2, False) }}{% endfor %}
}{% endif %}