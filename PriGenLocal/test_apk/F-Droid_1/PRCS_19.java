/* Application Package Name: org.fdroid.fdroid */
class PRCS_19 {
/**
org.fdroid.fdroid.nearby.WifiStateChangeService;run()V
*/

    public void run()
    {
        android.os.Process.setThreadPriority(19);
        try {
            org.fdroid.fdroid.FDroidApp.initWifiSettings();
            org.fdroid.fdroid.Utils.debugLog("WifiStateChangeService", "Checking wifi state (in background thread).");
            boolean v1_1 = org.fdroid.fdroid.nearby.WifiStateChangeService.-$$Nest$fgetwifiManager(this.this$0).getWifiState();
            boolean v3_0 = 0;
            int v5_0 = 0;
            String v4_0 = 0;
        } catch (boolean v1_3) {
            android.util.Log.e("WifiStateChangeService", "Unable to configure a fingerprint or HTTPS for the local repo", v1_3);
            android.content.Intent v0_2 = new android.content.Intent("org.fdroid.fdroid.action.WIFI_CHANGE");
            v0_2.putExtra("wifiStateChangeStatus", org.fdroid.fdroid.nearby.WifiStateChangeService.-$$Nest$sfgetwifiState());
            androidx.localbroadcastmanager.content.LocalBroadcastManager.getInstance(this.this$0.getApplicationContext()).sendBroadcast(v0_2);
            return;
        } catch (org.fdroid.fdroid.nearby.LocalRepoKeyStore$InitException) {
            org.fdroid.fdroid.Utils.debugLog("WifiStateChangeService", "interrupted");
            return;
        }
        while (org.fdroid.fdroid.FDroidApp.ipAddressString == null) {
            if (!this.isInterrupted()) {
                if (v1_1 != 3) {
                    if ((v1_1 == 1) || ((!v1_1) || (v1_1 == 4))) {
                        org.fdroid.fdroid.nearby.WifiStateChangeService.-$$Nest$msetIpInfoFromNetworkInterface(this.this$0);
                        if (org.fdroid.fdroid.FDroidApp.ipAddressString == null) {
                            return;
                        }
                    }
                } else {
                    v4_0 = org.fdroid.fdroid.nearby.WifiStateChangeService.-$$Nest$fgetwifiManager(this.this$0).getConnectionInfo();
                    org.fdroid.fdroid.FDroidApp.ipAddressString = org.fdroid.fdroid.nearby.WifiStateChangeService.formatIpAddress(v4_0.getIpAddress());
                    org.fdroid.fdroid.nearby.WifiStateChangeService.-$$Nest$msetSsid(this.this$0, v4_0);
                    String v6_5 = org.fdroid.fdroid.nearby.WifiStateChangeService.-$$Nest$fgetwifiManager(this.this$0).getDhcpInfo();
                    if (v6_5 != null) {
                        String v6_7 = org.fdroid.fdroid.nearby.WifiStateChangeService.formatIpAddress(v6_5.netmask);
                        if ((!android.text.TextUtils.isEmpty(org.fdroid.fdroid.FDroidApp.ipAddressString)) && (v6_7 != null)) {
                            try {
                                org.fdroid.fdroid.FDroidApp.subnetInfo = new org.apache.commons.net.util.SubnetUtils(org.fdroid.fdroid.FDroidApp.ipAddressString, v6_7).getInfo();
                            } catch (String v6_9) {
                                v6_9.printStackTrace();
                            }
                        }
                    }
                    if ((org.fdroid.fdroid.FDroidApp.ipAddressString == null) || (org.fdroid.fdroid.FDroidApp.subnetInfo == org.fdroid.fdroid.FDroidApp.UNSET_SUBNET_INFO)) {
                        org.fdroid.fdroid.nearby.WifiStateChangeService.-$$Nest$msetIpInfoFromNetworkInterface(this.this$0);
                    }
                }
                if (v5_0 <= 120) {
                    v5_0++;
                    if (org.fdroid.fdroid.FDroidApp.ipAddressString == null) {
                        Thread.sleep(1000);
                        org.fdroid.fdroid.Utils.debugLog("WifiStateChangeService", "waiting for an IP address...");
                    }
                } else {
                    return;
                }
            } else {
                return;
            }
        }
        if (!this.isInterrupted()) {
            boolean v1_13;
            org.fdroid.fdroid.nearby.WifiStateChangeService.-$$Nest$msetSsid(this.this$0, v4_0);
            if (!org.fdroid.fdroid.Preferences.get().isLocalRepoHttpsEnabled()) {
                v1_13 = "http";
            } else {
                v1_13 = "https";
            }
            String v4_2 = this.this$0.getApplicationContext();
            org.apache.commons.net.util.SubnetUtils v7_6 = new Object[3];
            v7_6[0] = v1_13;
            v7_6[1] = org.fdroid.fdroid.FDroidApp.ipAddressString;
            v7_6[2] = Integer.valueOf(org.fdroid.fdroid.FDroidApp.port);
            boolean v1_18 = String.format(java.util.Locale.ENGLISH, "%s://%s:%d/fdroid/repo", v7_6);
            org.fdroid.fdroid.nearby.LocalRepoKeyStore v2_4 = org.fdroid.fdroid.nearby.LocalRepoKeyStore.get(v4_2);
            int v5_2 = v2_4.getCertificate();
            if (v5_2 != 0) {
                v3_0 = org.fdroid.fdroid.Hasher.hex(v5_2).toLowerCase(java.util.Locale.US);
            } else {
            }
            boolean v1_19 = org.fdroid.fdroid.FDroidApp.createSwapRepo(v1_18, v3_0);
            if (!this.isInterrupted()) {
                org.fdroid.fdroid.nearby.LocalRepoManager.get(v4_2).writeIndexPage(org.fdroid.fdroid.Utils.getSharingUri(org.fdroid.fdroid.FDroidApp.repo).toString());
                if (!this.isInterrupted()) {
                    org.fdroid.fdroid.FDroidApp.repo = v1_19;
                    if (!org.fdroid.fdroid.Preferences.get().isLocalRepoHttpsEnabled()) {
                        v0_2 = new android.content.Intent("org.fdroid.fdroid.action.WIFI_CHANGE");
                        v0_2.putExtra("wifiStateChangeStatus", org.fdroid.fdroid.nearby.WifiStateChangeService.-$$Nest$sfgetwifiState());
                        androidx.localbroadcastmanager.content.LocalBroadcastManager.getInstance(this.this$0.getApplicationContext()).sendBroadcast(v0_2);
                        return;
                    } else {
                        v2_4.setupHTTPSCertificate();
                        v0_2 = new android.content.Intent("org.fdroid.fdroid.action.WIFI_CHANGE");
                        v0_2.putExtra("wifiStateChangeStatus", org.fdroid.fdroid.nearby.WifiStateChangeService.-$$Nest$sfgetwifiState());
                        androidx.localbroadcastmanager.content.LocalBroadcastManager.getInstance(this.this$0.getApplicationContext()).sendBroadcast(v0_2);
                        return;
                    }
                } else {
                    return;
                }
            } else {
                return;
            }
        } else {
            return;
        }
    }


}
