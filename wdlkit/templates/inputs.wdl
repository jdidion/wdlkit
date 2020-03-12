input {{ "{" }}{% for input in inputs %}
  {{ input.type }} {{ input.name}}{% if input.expr %} = {{ input.expr }}{% endif %}{% endfor %}
}