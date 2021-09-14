
resource "tls_private_key" "test_db_key" {
  algorithm = "RSA"
  rsa_bits  = 2048
}

resource "aws_key_pair" "generated_key" {
  key_name   = "test_db_key"
  public_key = tls_private_key.test_db_key.public_key_openssh
}

resource "aws_instance" "ec2" {
  ami                         = "ami-087c17d1fe0178315"
  associate_public_ip_address = true
  instance_type               = "t2.micro"
  key_name                    = aws_key_pair.ec2.key_name
  subnet_id                   = aws_default_subnet.default_subnet_a.id

  vpc_security_group_ids = [
    aws_security_group.ec2.id,
  ]

  tags = local.tags

}

resource "null_resource" "ssh_ec2_connection" {
  depends_on = [aws_instance.ec2.public_ip, tls_private_key.test_db_key]
  connection {
    type        = "ssh"
    host        = aws_instance.ec2.public_ip
    user        = "ec2-user"
    port        = "22"
    private_key = file(tls_private_key.test_db_key.private_key_pem)
    agent       = false
  }

  provisioner "remote-exec" {
    inline = [
      "sudo yum update -y",
    ]
  }
}
