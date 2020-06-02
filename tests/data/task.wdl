version 1.0

task simple {
  input {
    Int i
    String s = "hello"
    Map[String, Int] foo = {"x": 0}
  }

  String bork = "boink"
  Int z = 5

  command <<<
  echo ~{i}
  echo ~{i} > output
  >>>

  output {
    File output_file = "output"
  }

  runtime {
    docker: "ubuntu:latest"
  }

  meta {
    foo: "bar"
  }

  parameter_meta {
    i: {
      description: "A number"
    }
  }
}