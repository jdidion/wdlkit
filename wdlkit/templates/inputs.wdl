input {{ "{" }}{% for input in inputs %}
  {{ input.type }} {{ input.name}}{% if input.expr %} = {{ format_expression(input.expr) }}{% endif %}{% endfor %}
}