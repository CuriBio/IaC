
resource "tls_private_key" "example" {
  algorithm = "RSA"
  rsa_bits  = 2048
}


resource "aws_instance" "ec2" {
  ami                         = "ami-087c17d1fe0178315"
  associate_public_ip_address = true
  instance_type               = "t2.micro"
  key_name                    = "db_key_pair"
  subnet_id                   = aws_default_subnet.default_subnet_a.id

  vpc_security_group_ids = [aws_default_vpc.default_vpc.default_security_group_id]

  tags = local.tags

}
