runtime {{ "{" }}{% if runtime %}{% for item in runtime.items() %}
  {{ item[0] }}: {{ item[1] }}{% endfor %}{% endif %}
}