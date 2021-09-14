
resource "tls_private_key" "test_db_key" {
  algorithm = "RSA"
  rsa_bits  = 2048
}

resource "aws_key_pair" "ec2" {
  key_name   = "test_db_key"
  public_key = tls_private_key.test_db_key.public_key_openssh
}

resource "aws_instance" "ec2" {
  ami                         = "ami-087c17d1fe0178315"
  associate_public_ip_address = true
  instance_type               = "t2.micro"
  key_name                    = aws_key_pair.ec2.key_name
  subnet_id                   = aws_default_subnet.default_subnet_a.id

  vpc_security_group_ids = [aws_security_group.ec2.id]

  tags = local.tags

}

resource "null_resource" "ssh_ec2_connection" {
  depends_on = [aws_instance.ec2, tls_private_key.test_db_key, module.db]
  connection {
    type        = "ssh"
    host        = aws_instance.ec2.public_ip
    user        = "ec2-user"
    port        = "22"
    private_key = tls_private_key.test_db_key.private_key_pem
    agent       = false
    timeout     = "60s"
  }

  provisioner "remote-exec" {
    inline = [
      "sudo yum update -y",
      "sudo rpm -Uvh https://dev.mysql.com/get/mysql57-community-release-el7-11.noarch.rpm",
      "sudo yum install mysql-community-server",
      "sudo systemctl enable mysqld",
      "sudo systemctl start mysqld",
      "mysql -u ${format(var.db_username)} -p${format(var.db_password)} -h ${module.db.rds_cluster_instance_endpoints[0]} -P ${module.db.rds_cluster_port} < ${path.module}/schema.sql;",
    ]
  }
}
