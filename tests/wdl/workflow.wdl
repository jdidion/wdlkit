version 1.0

import "task.wdl" as simple

workflow test {
  input {
    Int i
    Boolean b = true
  }

  if (b) {
    call simple.simple {
      input: i = i
    }
  }

  output {
    File? output_file = simple.output_file
  }

  meta {
    description: "Test workflow"
  }

  parameter_meta {
    i: {
      description: "Integer"
    }
    b: {
      description: "Whether to call the task"
    }
  }
}