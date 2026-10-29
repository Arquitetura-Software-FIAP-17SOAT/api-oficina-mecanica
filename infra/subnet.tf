resource "aws_subnet" "subnet_public" {
  count                   = 3
  vpc_id                  = aws_vpc.vpc_fiap.id
  cidr_block              = cidrsubnet(aws_vpc.vpc_fiap.cidr_block, 4, count.index)
  map_public_ip_on_launch = true
  availability_zone       = "${var.region_default}${["a", "b", "c"][count.index]}"
}