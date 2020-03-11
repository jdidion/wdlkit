struct {{ value.name }} {{% for member in value.members %}
  {{member.type}} {{member.name}}{% endfor %}
}