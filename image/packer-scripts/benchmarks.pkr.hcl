
locals {
  rootdir = "${path.root}/../../"
}

variable "ssh_password" {
  type    = string
  default = "12345"
}

variable "ssh_username" {
  type    = string
  default = "gem5"
}



source "null" "remote" {
  ssh_host = "localhost"
  ssh_port = "5555"
  ssh_password     = "${var.ssh_password}"
  ssh_username     = "${var.ssh_username}"
  ssh_handshake_attempts = "10"
  # shutdown_command = "echo '${var.ssh_password}'|sudo -S shutdown -P now"
  communicator = "ssh"
}




build {
  sources = ["sources.null.remote"]
  # sources = ["sources.qemu.boot"]


  # Install Docker --------------------------
  provisioner "shell" {
    execute_command = "echo '${var.ssh_password}' | {{ .Vars }} sudo -E -S bash '{{ .Path }}'"
    scripts         = ["${local.rootdir}/image/scripts/install_docker.sh"]
  }




  ### Move the client to the VM
  provisioner "file" {
    destination = "http-client"
    source      = "${local.rootdir}/image/tmp/http-client"
  }

  provisioner "shell" {
    inline = [
      "chmod +x http-client",
    ]
  }

  ## Nodeapp provisioning --------------------------
  provisioner "file" {
    destination = "nodeapp.urls.tmpl"
    source      = "${local.rootdir}/benchmarks/nodeapp/urls.tmpl"
  }

  provisioner "file" {
    destination = "dc-nodeapp.yaml"
    source      = "${local.rootdir}/benchmarks/nodeapp/docker-compose.yaml"
  }


  provisioner "shell" {
    execute_command = "echo '${var.ssh_password}' | {{ .Vars }} sudo -E -S bash '{{ .Path }}'"
    inline = [
      "sudo docker compose -f dc-nodeapp.yaml pull",
      "sudo docker compose -f dc-nodeapp.yaml up -d",
      "sleep 10",
      "curl 0.0.0.0:9999/",
      "sudo docker compose -f dc-nodeapp.yaml down",
    ]
  }







  #### Shutdown the VM ###########
  provisioner "shell" {
    inline = [
      "sudo shutdown -h now",
    ]
    # expect_disconnect = true
    valid_exit_codes = [ 0, 2300218 ]

  }

}
