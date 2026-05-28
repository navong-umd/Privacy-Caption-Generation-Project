/* Application Package Name: org.fdroid.fdroid */
class PRCS_18 {
/**
org.fdroid.fdroid.nearby.WifiStateChangeService;doWork()Landroidx/work/ListenableWorker$Result;
*/

    public androidx.work.ListenableWorker$Result doWork()
    {
        int v1_1;
        android.os.Process.setThreadPriority(19);
        int v0_17 = this.getInputData().getInt("networkInfo", -1);
        if (v0_17 == -1) {
            v1_1 = 0;
        } else {
            v1_1 = android.net.NetworkInfo$State.values()[v0_17];
        }
        org.fdroid.fdroid.Utils.debugLog("WifiStateChangeService", "WiFi change service started.");
        StringBuilder v2_3 = ((android.net.wifi.WifiManager) androidx.core.content.ContextCompat.getSystemService(this.getApplicationContext(), android.net.wifi.WifiManager));
        this.wifiManager = v2_3;
        if (v2_3 != null) {
            org.fdroid.fdroid.nearby.WifiStateChangeService.wifiState = v2_3.getWifiState();
            StringBuilder v2_6 = new StringBuilder();
            v2_6.append("networkInfoStateInt == ");
            v2_6.append(v0_17);
            v2_6.append("  wifiState == ");
            v2_6.append(this.printWifiState(org.fdroid.fdroid.nearby.WifiStateChangeService.wifiState));
            org.fdroid.fdroid.Utils.debugLog("WifiStateChangeService", v2_6.toString());
            if (((v1_1 == 0) || ((v1_1 == android.net.NetworkInfo$State.CONNECTED) || (v1_1 == android.net.NetworkInfo$State.DISCONNECTED))) && ((org.fdroid.fdroid.nearby.WifiStateChangeService.previousWifiState != org.fdroid.fdroid.nearby.WifiStateChangeService.wifiState) && ((org.fdroid.fdroid.nearby.WifiStateChangeService.wifiState == 3) || ((org.fdroid.fdroid.nearby.WifiStateChangeService.wifiState == 0) || ((org.fdroid.fdroid.nearby.WifiStateChangeService.wifiState == 1) || (org.fdroid.fdroid.nearby.WifiStateChangeService.wifiState == 4)))))) {
                int v0_13 = org.fdroid.fdroid.nearby.WifiStateChangeService.wifiInfoThread;
                if (v0_13 != 0) {
                    v0_13.interrupt();
                }
                int v0_15 = new org.fdroid.fdroid.nearby.WifiStateChangeService$WifiInfoThread(this);
                org.fdroid.fdroid.nearby.WifiStateChangeService.wifiInfoThread = v0_15;
                v0_15.start();
            }
            return androidx.work.ListenableWorker$Result.success();
        } else {
            return androidx.work.ListenableWorker$Result.failure();
        }
    }


}
