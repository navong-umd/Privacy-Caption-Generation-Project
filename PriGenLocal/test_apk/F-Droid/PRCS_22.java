/*Application Package Name: org.fdroid.fdroid
class PRCS_22 {
/**
org.fdroid.fdroid.nearby.BonjourManager;isVpnActive(Landroid/content/Context;)Z
*/

    public static boolean isVpnActive(android.content.Context p1)
    {
        boolean v1_4 = ((android.net.ConnectivityManager) p1.getSystemService("connectivity"));
        boolean v1_5 = v1_4.getNetworkCapabilities(v1_4.getActiveNetwork());
        if (v1_5) {
            return v1_5.hasTransport(4);
        } else {
            return 0;
        }
    }

/**
org.fdroid.fdroid.nearby.BonjourManager;setVisible(Landroid/content/Context; Z)V
*/

    public static void setVisible(android.content.Context p1, boolean p2)
    {
        org.fdroid.fdroid.nearby.BonjourManager.context = new ref.WeakReference(p1);
        if ((org.fdroid.fdroid.nearby.BonjourManager.handler != null) && ((org.fdroid.fdroid.nearby.BonjourManager.handlerThread != null) && (org.fdroid.fdroid.nearby.BonjourManager.handlerThread.isAlive()))) {
            if (!org.fdroid.fdroid.nearby.BonjourManager.isVpnActive(p1)) {
                if (p2 == 0) {
                    org.fdroid.fdroid.nearby.BonjourManager.handler.sendEmptyMessage(144151873);
                } else {
                    org.fdroid.fdroid.nearby.BonjourManager.handler.sendEmptyMessage(4151873);
                }
            } else {
                org.fdroid.fdroid.nearby.BonjourManager.handler.sendEmptyMessage(72346752);
            }
            return;
        } else {
            android.util.Log.e("BonjourManager", "handlerThread is stopped, not changing visibility!");
            return;
        }
    }

/**
org.fdroid.fdroid.nearby.SwapService;restartWiFiServices()V
*/

    private void restartWiFiServices()
    {
        if (org.fdroid.fdroid.FDroidApp.ipAddressString == null) {
            org.fdroid.fdroid.nearby.BonjourManager.stop(this);
            org.fdroid.fdroid.nearby.LocalHTTPDManager.stop(this);
        } else {
            int v0_2;
            org.fdroid.fdroid.nearby.LocalHTTPDManager.restart(this);
            org.fdroid.fdroid.nearby.BonjourManager.restart(this);
            if ((!org.fdroid.fdroid.nearby.SwapService.getWifiVisibleUserPreference()) && (!org.fdroid.fdroid.nearby.SwapService.getHotspotActivatedUserPreference())) {
                v0_2 = 0;
            } else {
                v0_2 = 1;
            }
            org.fdroid.fdroid.nearby.BonjourManager.setVisible(this, v0_2);
        }
        return;
    }


}