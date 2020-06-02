scatter ({{ scatter.variable }} in {{ format_expression(scatter.expr) }}) {
  {{ body }}
}