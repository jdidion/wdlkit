output {{ "{" }}{% for output in outputs %}
  {{ output.type }} {{output.name}}{% if output.expr %} = {{ output.expr }}{% endif %}{% endfor %}
}