call {{ ".".join(value.callee_id) }}{% if value.name != value.callee_id[-1] %} as {{ value.name }}{% endif %} {{ "{" }}{% if value.inputs %}
  inputs:{% for inp in value.inputs.items() %}
    {{ inp[0] }} = {{ inp[1] }}{% endfor %}
}