
locals {
  rootdir = "${path.root}/../../"
}

variable "ssh_password" {
  type    = string
  default = "root"
}

variable "ssh_username" {
  type    = string
  default = "root"
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

  # 
  provisioner "shell" {
    execute_command = "echo '${var.ssh_password}' | {{ .Vars }} sudo -E -S bash '{{ .Path }}'"
    scripts         = ["${local.rootdir}/benchmarks/fleetbench/install_fleetbench.sh"]
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
