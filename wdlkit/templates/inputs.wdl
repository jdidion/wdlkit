input {{ "{" }}{% for input in inputs %}
  {{ format_type(input.type) }} {{ input.name}}{% if input.expr %} = {{ format_expression(input.expr) }}{% endif %}{% endfor %}
}