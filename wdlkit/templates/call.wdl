call {{ ".".join(call.callee_id) }}{% if call.name != call.callee_id[-1] %} as {{ call.name }}{% endif %} {{ "{" }}{% if call.inputs %}
  input:{% for inp in call.inputs.items() %}
    {{ inp[0] }} = {{ format_expression(inp[1]) }}{% endfor %}{% endif %}
}