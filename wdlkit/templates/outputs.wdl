output {{ "{" }}{% for output in outputs %}
  {{ output.type }} {{output.name}}{% if output.expr %} = {{ format_expression(output.expr) }}{% endif %}{% endfor %}
}