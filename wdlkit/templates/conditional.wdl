if ({{ format_expression(conditional.expr) }}) {
  {{ body | trim() | indent(2, False) }}
}