struct {{ struct.name }} {{% for member in struct.members %}
  {{member.type}} {{member.name}}{% endfor %}
}