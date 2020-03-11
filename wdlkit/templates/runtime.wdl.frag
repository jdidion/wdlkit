runtime {{ "{" }}{% if value %}{% for item in value.items() %}
  {{ item[0] }}: {{ item[1] }}{% endfor %}{% endif %}
}