/* Application Package Name: org.fdroid.fdroid */
class PRCS_20 {
/**
org.fdroid.fdroid.nearby.WifiStateChangeService;setSsid(Landroid/net/wifi/WifiInfo;)V
*/

    private void setSsid(android.net.wifi.WifiInfo p8)
    {
        String v0_0 = this.getApplicationContext();
        if ((p8 == null) || (p8.getBSSID() == null)) {
            String v8_9 = cc.mvdan.accesspoint.WifiApControl.getInstance(v0_0);
            String v2_0 = new StringBuilder();
            v2_0.append("WifiApControl: ");
            v2_0.append(v8_9);
            org.fdroid.fdroid.Utils.debugLog("WifiStateChangeService", v2_0.toString());
            if ((v8_9 != null) || (org.fdroid.fdroid.FDroidApp.ipAddressString == null)) {
                if ((v8_9 != null) && (v8_9.isEnabled())) {
                    String v8_1 = v8_9.getConfiguration();
                    String v5_3 = new StringBuilder();
                    v5_3.append("WifiConfiguration: ");
                    v5_3.append(v8_1);
                    org.fdroid.fdroid.Utils.debugLog("WifiStateChangeService", v5_3.toString());
                    if (v8_1 != null) {
                        if (!v8_1.hiddenSSID) {
                            org.fdroid.fdroid.FDroidApp.ssid = v8_1.SSID;
                        } else {
                            org.fdroid.fdroid.FDroidApp.ssid = v0_0.getString(org.fdroid.fdroid.R$string.swap_hidden_wifi_ssid);
                        }
                        org.fdroid.fdroid.FDroidApp.bssid = v8_1.BSSID;
                    } else {
                        int v1_3 = new Object[1];
                        v1_3[0] = "";
                        org.fdroid.fdroid.FDroidApp.ssid = v0_0.getString(org.fdroid.fdroid.R$string.swap_active_hotspot, v1_3);
                        org.fdroid.fdroid.FDroidApp.bssid = "";
                        return;
                    }
                }
            } else {
                String v8_6 = this.wifiManager.getConnectionInfo();
                if ((v8_6 == null) || (v8_6.getBSSID() == null)) {
                    int v1_5 = new Object[1];
                    v1_5[0] = "";
                    org.fdroid.fdroid.FDroidApp.ssid = v0_0.getString(org.fdroid.fdroid.R$string.swap_active_hotspot, v1_5);
                } else {
                    this.setSsid(v8_6);
                }
            }
        } else {
            String v2_4 = p8.getSSID();
            String v3_3 = new StringBuilder();
            v3_3.append("Have wifi info, connected to ");
            v3_3.append(v2_4);
            org.fdroid.fdroid.Utils.debugLog("WifiStateChangeService", v3_3.toString());
            if (v2_4 != null) {
                org.fdroid.fdroid.FDroidApp.ssid = v2_4.replaceAll("^\"(.*)\"$", "$1");
            } else {
                org.fdroid.fdroid.FDroidApp.ssid = v0_0.getString(org.fdroid.fdroid.R$string.swap_blank_wifi_ssid);
            }
            org.fdroid.fdroid.FDroidApp.bssid = p8.getBSSID();
        }
        return;
    }


}
