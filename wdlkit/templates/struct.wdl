struct {{ struct.name }} {{'{'}}{% for member_name, member_type in struct.members.items() %}
  {{ format_type(member_type) }} {{ member_name }}{% endfor %}
}