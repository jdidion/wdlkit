runtime {{ "{" }}{% if runtime %}{% for item in runtime.items() %}
  {{ item[0] }}: {{ format_expression(item[1]) }}{% endfor %}{% endif %}
}