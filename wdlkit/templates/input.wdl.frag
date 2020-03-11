input {{ "{" }}{% for input in value %}
  {{ input.type }} {{ input.name}}{% if input.expr %} = {{ input.expr }}{% endif %}{% endfor %}
}