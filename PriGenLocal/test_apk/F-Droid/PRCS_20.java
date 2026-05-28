/*Application Package Name: org.fdroid.fdroid
class PRCS_20 {
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
org.fdroid.fdroid.nearby.SwapWorkflowActivity;lambda$setUpStartVisibility$12(Landroid/widget/CompoundButton; Z)V
*/

    private synthetic void lambda$setUpStartVisibility$12(android.widget.CompoundButton p3, boolean p4)
    {
        p3 = this.getApplicationContext();
        if (p4) {
            android.net.wifi.WifiManager v0_1 = this.wifiApControl;
            if ((v0_1 == null) || (!v0_1.isEnabled())) {
                if (android.os.Build$VERSION.SDK_INT <= 28) {
                    this.wifiManager.setWifiEnabled(1);
                }
            } else {
                this.setupWifiAP();
            }
            org.fdroid.fdroid.nearby.BonjourManager.start(p3);
        }
        org.fdroid.fdroid.nearby.BonjourManager.setVisible(p3, p4);
        org.fdroid.fdroid.nearby.SwapService.putWifiVisibleUserPreference(p4);
        return;
    }


}