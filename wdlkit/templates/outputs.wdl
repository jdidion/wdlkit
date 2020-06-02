output {{ "{" }}{% for output in outputs %}
  {{ format_type(output.type) }} {{output.name}}{% if output.expr %} = {{ format_expression(output.expr) }}{% endif %}{% endfor %}
}