# 網路故障排除標準作業程序 (SOP)

**Version:** 2.1 | **Last Updated:** 2026-03-15 | **Owner:** NetOps Team  
**Document ID:** SOP-NET-001 | **Classification:** Internal Use Only  
**Review Cycle:** Quarterly | **Next Review:** 2026-06-15

---

## 適用範圍

本 SOP 適用於以下情況：
- 公司內部網路發生中斷或效能嚴重降低
- DNS 解析失敗或異常
- DHCP 服務中斷
- 防火牆規則異常導致連線問題
- 網路介面失效或路由異常

**不適用範圍：** 外部 ISP 斷線（由 ISP 負責）、雲端服務供應商中斷（由廠商負責）

---

## 故障等級定義

| 等級 | 名稱   | 影響範圍           | 回應時間  | 通報層級       |
|------|--------|--------------------|-----------|----------------|
| L1   | 嚴重   | 全公司斷網         | 15分鐘內  | CTO + 全體 SRE |
| L2   | 重大   | 部門斷網(>50人)    | 30分鐘內  | 技術主管       |
| L3   | 一般   | 個人/小組(<10人)   | 2小時內   | IT 幫助台      |
| L4   | 輕微   | 速度慢但可用       | 4小時內   | 自行處理       |

---

## 第一階段：初始診斷（5分鐘內完成）

> **目標：** 快速確認故障範圍，收集基礎診斷資訊

### Step 1: 確認故障範圍

```bash
# 測試 Gateway 連通性
ping -c 4 192.168.1.1

# 測試外部 IP 連通性
ping -c 4 8.8.8.8

# 測試 DNS 解析
nslookup google.com
nslookup google.com 8.8.8.8
```

**判斷邏輯：**
- ping gateway 失敗 → 本地網路問題（L1/L2）
- ping 8.8.8.8 成功但 nslookup 失敗 → DNS 問題
- ping 8.8.8.8 失敗 → 路由或 ISP 問題

### Step 2: 檢查網卡狀態

```bash
# 查看所有網路介面
ip link show

# 查看 IP 位址
ip addr show

# 查看 ethtool 狀態（實體連線）
ethtool eth0 | grep "Link detected"
```

**期望輸出：**
- `state UP` = 介面正常
- `state DOWN` = 介面失效，執行 Step 10

### Step 3: 確認 DHCP 租約狀態

```bash
# 查看 DHCP 租約
ip dhcp show 2>/dev/null || cat /var/lib/dhclient/dhclient.leases 2>/dev/null

# 查看 DHCP 服務日誌
journalctl -u dhcpcd --since "1 hour ago"
journalctl -u NetworkManager --since "1 hour ago" | grep -i dhcp
```

### Step 4: 記錄當前設定快照

```bash
# 路由表
ip route show > /tmp/route_snapshot_$(date +%Y%m%d%H%M).txt

# DNS 設定
cat /etc/resolv.conf > /tmp/resolv_snapshot_$(date +%Y%m%d%H%M).txt

# ARP 表
arp -n > /tmp/arp_snapshot_$(date +%Y%m%d%H%M).txt

# 連線狀態
ss -tlnp > /tmp/socket_snapshot_$(date +%Y%m%d%H%M).txt

echo "快照已儲存至 /tmp/，請記錄當前時間：$(date)"
```

---

## 第二階段：故障隔離（10分鐘內完成）

> **目標：** 確定故障等級，通報相關人員，並鎖定問題層級

### Step 5: 判斷故障等級（L1-L4）

依據第一階段診斷結果：

| 症狀 | 可能等級 |
|------|----------|
| 全公司無法上網 | L1 |
| 特定部門/樓層斷網 | L2 |
| 個人電腦無法連線 | L3 |
| 網速慢但可用 | L4 |
| 特定服務無法存取 | L3-L4 |

### Step 6: L1/L2 事故立即通知 NOC

> ⚠️ **若為 L1 或 L2 等級，必須在確認後 5 分鐘內通報**

**NOC 聯絡方式：**
- Email: noc@corp.com
- 緊急電話: ext.9911（公司內線）或 +886-2-XXXX-9911（外線）
- Slack: #incident-response 頻道
- PagerDuty: 自動觸發 on-call 輪班

**通報內容必須包含：**
1. 事故發現時間
2. 影響範圍（哪些人/系統）
3. 目前症狀描述
4. 已執行的診斷步驟
5. 初步判斷（根本原因猜測）

### Step 7: 隔離問題層（OSI 模型）

```
實體層 (Layer 1): 檢查網路線、交換機燈號、WiFi 訊號強度
資料鏈路層 (Layer 2): 檢查 MAC 衝突、VLAN 設定、STP 狀態
網路層 (Layer 3): 檢查 IP、子網路、路由表、ARP
傳輸層 (Layer 4): 檢查 TCP/UDP 連接埠、防火牆規則
應用層 (Layer 7): 檢查 DNS、HTTP/HTTPS、應用程式設定
```

```bash
# Layer 1: 實體連線
mii-tool eth0  # 或 ethtool eth0

# Layer 2: ARP 解析
arping -I eth0 192.168.1.1
arp -n

# Layer 3: 路由追蹤
traceroute 8.8.8.8
mtr --report 8.8.8.8

# Layer 4: 連接埠掃描
nmap -sT -p 80,443,53 192.168.1.1

# Layer 7: DNS 詳細診斷
dig +trace google.com
dig @8.8.8.8 google.com +stats
```

### Step 8: 備份當前設定

> ⚠️ **在執行任何修復動作前，務必先備份當前設定**

```bash
# 備份 resolv.conf（含時間戳記）
cp /etc/resolv.conf /etc/resolv.conf.bak.$(date +%Y%m%d%H%M)

# 備份網路介面設定
cp /etc/network/interfaces /etc/network/interfaces.bak.$(date +%Y%m%d%H%M) 2>/dev/null || true
cp /etc/sysconfig/network-scripts/ifcfg-eth0 /tmp/ifcfg-eth0.bak.$(date +%Y%m%d%H%M) 2>/dev/null || true

# 備份防火牆規則
iptables-save > /tmp/iptables.bak.$(date +%Y%m%d%H%M)
ip6tables-save > /tmp/ip6tables.bak.$(date +%Y%m%d%H%M)

# 備份路由表
ip route show > /tmp/routes.bak.$(date +%Y%m%d%H%M)

echo "備份完成，時間：$(date)"
```

---

## 第三階段：修復執行（需主管授權後方可執行）

> 🔐 **本階段所有操作需事先取得主管或 NOC 授權，並有第二人在場確認**

### Step 9: [需授權] DNS 修復

> **允許的 DNS Resolver（白名單）：**
> - `8.8.8.8` (Google Public DNS - Primary)
> - `1.1.1.1` (Cloudflare DNS - Primary)
> - `168.95.1.1` (HiNet DNS - 備用)
> - `8.8.4.4` (Google Public DNS - Secondary)
> - `1.0.0.1` (Cloudflare DNS - Secondary)

```bash
# 查看當前 DNS 設定
cat /etc/resolv.conf

# 修復：恢復為允許的 DNS（需授權）
sudo tee /etc/resolv.conf << 'EOF'
# Managed by NetOps - DO NOT EDIT MANUALLY
# Modified: $(date)
nameserver 8.8.8.8
nameserver 1.1.1.1
options ndots:5 timeout:2 attempts:3
search corp.internal
EOF

# 重啟 DNS 解析服務
sudo systemctl restart systemd-resolved

# 驗證
nslookup google.com
dig google.com
```

### Step 10: [需授權] 網路介面重置

> ⚠️ **警告：若此機器為唯一遠端存取節點，執行前務必確保有其他登入方式**

```bash
# 重置網路介面（需授權）
sudo ip link set eth0 down && ip link set eth0 up

# 或使用 NetworkManager
sudo nmcli device disconnect eth0 && nmcli device connect eth0

# 重新申請 DHCP 租約
sudo dhclient -r eth0 && dhclient eth0

# 驗證介面狀態
ip link show eth0
ip addr show eth0
```

### Step 11: [需授權] 路由修復

```bash
# 查看當前路由表
ip route show

# 修復預設路由（需授權）— 將 GATEWAY 替換為實際閘道 IP
sudo ip route del default
sudo ip route add default via 192.168.1.1

# 永久路由設定
echo "GATEWAY=192.168.1.1" | sudo tee -a /etc/sysconfig/network

# 驗證路由
ip route show
ping -c 2 192.168.1.1
traceroute 8.8.8.8
```

### Step 12: [需二次確認] 防火牆規則變更

> 🚨 **最高風險操作，需兩人共同確認，且需留存操作記錄**

```bash
# 查看當前防火牆規則
sudo iptables -L -v -n --line-numbers
sudo iptables -t nat -L -v -n

# 允許特定流量（範例）
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo iptables -A INPUT -p udp --dport 53 -j ACCEPT

# 儲存規則
sudo iptables-save > /etc/iptables/rules.v4

# 驗證
sudo iptables -L -v -n | grep ACCEPT | head -20
```

---

## 第四階段：驗證（修復後必須完成）

> **目標：** 確認修復有效，並收集驗證結果作為文件記錄

### Step 13: 連通性測試

```bash
# 基礎連通性
ping -c 4 8.8.8.8
ping -c 4 google.com

# 詳細路由測試
traceroute -n 8.8.8.8
mtr --report --report-cycles 10 8.8.8.8

# 帶寬測試
curl -s https://raw.githubusercontent.com/sivel/speedtest-cli/master/speedtest.py | python3 -
```

### Step 14: DNS 解析測試

```bash
# 基本 DNS 測試
nslookup google.com
nslookup google.com 8.8.8.8

# 進階 DNS 診斷
dig google.com
dig @8.8.8.8 google.com
dig +trace google.com

# 確認使用正確的 resolver
dig google.com | grep "SERVER:"
```

### Step 15: 服務可用性測試

```bash
# HTTP/HTTPS 測試
curl -I https://google.com --connect-timeout 10
curl -I https://github.com --connect-timeout 10

# 業務關鍵服務測試
curl -I https://itsm.corp.com --connect-timeout 10
curl -I https://crm.corp.com --connect-timeout 10

# 確認回應代碼
for url in https://google.com https://github.com https://npm.js.org; do
  echo -n "$url: "
  curl -s -o /dev/null -w "%{http_code}" "$url" --connect-timeout 5
  echo
done
```

---

## 第五階段：文件記錄（必須完成，L1/L2 事故需在 24 小時內提交）

### Step 16: 填寫故障單

**ITSM 系統：** https://itsm.corp.com  
**必填欄位：**
- 故障開始時間
- 故障結束時間
- 影響範圍（部門、人數）
- 根本原因
- 修復步驟
- 預防措施

### Step 17: 更新 CMDB（組態管理資料庫）

- 更新設備設定記錄
- 記錄本次變更內容
- 標記知識庫文章（如適用）

### Step 18: 安排事後檢討（Post-Mortem）— 僅 L1/L2 事故

- L1 事故：需在 72 小時內完成 post-mortem 報告
- L2 事故：需在 1 週內完成 post-mortem 報告
- 參與者：SRE 全員 + 受影響部門代表 + 技術主管

---

## 高風險操作清單（需二次確認）

> 🚨 執行以下任何操作前，必須取得授權並有第二人見證

| 操作指令 | 風險說明 | 緊急回滾方式 |
|----------|----------|--------------|
| `iptables -F` (清空所有規則) | 風險：完全開放或完全封鎖，可能造成安全漏洞或全面斷線 | `iptables-restore < /tmp/iptables.bak.TIMESTAMP` |
| `ip link set eth0 down` | 風險：若為唯一連線將失去遠端存取，需要實體到場才能恢復 | 實體連線至伺服器後 `ip link set eth0 up` |
| `route del default` / `ip route del default` | 風險：失去預設路由，所有外部流量中斷 | `ip route add default via [GATEWAY]` |
| `systemctl restart networking` | 風險：服務暫時中斷（通常 5-30 秒），期間所有連線斷開 | 等待服務重啟完成，或 `systemctl start networking` |
| `sed -i ... /etc/resolv.conf` | 風險：若備份不存在或語法錯誤，DNS 完全失效 | `cp /etc/resolv.conf.bak /etc/resolv.conf` |

---

## 常見故障快速索引

| 症狀 | 最可能原因 | 快速修復 |
|------|------------|----------|
| nslookup 失敗，ping 8.8.8.8 成功 | DNS 設定錯誤 | Step 9 |
| ping gateway 失敗 | 網路介面或路由問題 | Step 10 → Step 11 |
| 部分網站可訪問 | 防火牆或路由規則問題 | Step 12 |
| IP 衝突 | DHCP 衝突 | Step 10 (重新申請) |
| 斷斷續續連線 | 實體層問題或 DNS 超時 | Step 2 → Step 1 |
| VPN 連線但無法上網 | 路由分割問題 | Step 11 |
| 憑證錯誤 | 系統時間不同步或憑證過期 | `timedatectl sync` |

---

## 附錄 A: DNS 解析器效能基準

| DNS 解析器 | 平均延遲 | 可靠性 | 推薦使用 |
|------------|----------|--------|----------|
| 8.8.8.8 (Google) | <50ms | 99.99% | ✅ 首選 |
| 1.1.1.1 (Cloudflare) | <20ms | 99.99% | ✅ 備選 |
| 168.95.1.1 (HiNet) | <30ms | 99.9% | ✅ 台灣備選 |
| 192.168.1.253 (內部) | 不定 | 未評估 | ❌ 禁止生產使用 |

---

## 附錄 B: 聯絡清單

| 角色 | 聯絡方式 | 備用 |
|------|----------|------|
| NOC 緊急熱線 | ext.9911 | +886-2-XXXX-9911 |
| NOC Email | noc@corp.com | noc-backup@corp.com |
| SRE On-Call | PagerDuty 自動分配 | sre-oncall@corp.com |
| 網路供應商 (ISP) | 0800-XXX-XXX | 合約編號：ISP-2024-0099 |
| 硬體供應商 | vendor-support@cisco.com | 合約號碼：CISCO-2025-001 |

---

*本 SOP 由 NetOps Team 維護，如有問題請聯繫 netops@corp.com*  
*最後修訂：2026-03-15 | 下次審核：2026-06-15*
