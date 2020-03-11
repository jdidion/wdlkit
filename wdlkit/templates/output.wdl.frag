output {{ "{" }}{% for output in value %}
  {{ output.type }} {{output.name}}{% if output.expr %} = {{ output.expr }}{% endif %}{% endfor %}
}