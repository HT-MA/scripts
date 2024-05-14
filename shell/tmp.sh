#/bin/bash
master="192.168.43.143"
node01="192.168.43.144"
node02="192.168.43.145"

# 设置上面三台服务器的hostname位置
for i in $master $node01 $node02
do
  ssh $i "hostnamectl set-hostname $i"
done

# g关闭防火墙
for i in $master $node01 $node02
do
  ssh $i "systemctl stop firewalld && systemctl disable firewalld"
done

# 关闭swap
for i in $master $node01 $node02
do
  ssh $i "swapoff -a && sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab"
done

# 互作本地解析
for i in $master $node01 $node02
do
  ssh $i "echo '192.168.43.143 master' >> /etc/hosts"
  ssh $i "echo '192.168.43.144 node01' >> /etc/hosts"
  ssh $i "echo '192.168.43.145 node02' >> /etc/hosts"
done

# 关闭selinux
for i in $master $node01 $node02
do
  ssh $i "setenforce 0 && sed -i 's/^SELINUX=.*/SELINUX=disabled/' /etc/selinux/config"
done

# 配置桥接
for i in $master $node01 $node02
do
  ssh $i "cat <<EOF > /etc/sysconfig/network-scripts/ifcfg-ens33
DEVICE=ens33
BOOTPROTO=none
ONBOOT=yes
TYPE=Bridge
EOF"
done

# 加载br_netfilter模块
for i in $master $node01 $node02
do
  ssh $i "modprobe br_netfilter"
done

# 设置时间同步
for i in $master $node01 $node02
do
  ssh $i "yum install -y ntpdate && ntpdate time.windows.com && hwclock -w"
done

# 允许iptables检查桥接流量
for i in $master $node01 $node02
do
  ssh $i "echo 'net.bridge.bridge-nf-call-ip6tables = 1' >> /etc/sysctl.conf"
  ssh $i "echo 'net.bridge.bridge-nf-call-iptables = 1' >> /etc/sysctl.conf"
  ssh $i "sysctl -p"
done

# 安装kubeadm、kubelet、kubectl
for i in $master $node01 $node02
do
  ssh $i "yum install -y kubelet-1.26.0 kubeadm-1.26.0 kubectl-1.26.0"
  ssh $i "systemctl enable kubelet && systemctl start kubelet"
done


