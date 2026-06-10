package kubernetes.validating

import future.keywords.in

deny[msg] {
  container := input.request.object.spec.containers[_]
  not container.resources.limits
  msg := sprintf("Container '%v' has no resource limits set", [container.name])
}

deny[msg] {
  container := input.request.object.spec.containers[_]
  container.image == "nginx:latest"
  msg := "Using 'latest' tag is not allowed"
}
