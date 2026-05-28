/*Application Package Name: org.fdroid.fdroid
class PRCS_32 {
/**
org.fdroid.fdroid.nearby.SwapWorkflowActivity;lambda$promptToSelectWifiNetwork$4(Landroid/content/DialogInterface; I)V
*/

    private synthetic void lambda$promptToSelectWifiNetwork$4(android.content.DialogInterface p1, int p2)
    {
        org.fdroid.fdroid.nearby.SwapService.putWifiEnabledBeforeSwap(this.wifiManager.isWifiEnabled());
        if (android.os.Build$VERSION.SDK_INT <= 28) {
            this.wifiManager.setWifiEnabled(1);
        }
        android.content.Intent v1_2 = new android.content.Intent("android.net.wifi.PICK_WIFI_NETWORK");
        v1_2.setFlags(268435456);
        this.startActivity(v1_2);
        return;
    }

/**
org.fdroid.fdroid.nearby.SwapWorkflowActivity;$r8$lambda$MfcA6b8Lk6hyLtjJNXNmsN0JC3I(Lorg/fdroid/fdroid/nearby/SwapWorkflowActivity; Landroid/content/DialogInterface; I)V
*/

    public static synthetic void $r8$lambda$MfcA6b8Lk6hyLtjJNXNmsN0JC3I(org.fdroid.fdroid.nearby.SwapWorkflowActivity p0, android.content.DialogInterface p1, int p2)
    {
        p0.lambda$promptToSelectWifiNetwork$4(p1, p2);
        return;
    }

/**
org.fdroid.fdroid.nearby.SwapWorkflowActivity;onClick(Landroid/content/DialogInterface; I)V
*/

    public final void onClick(android.content.DialogInterface p2, int p3)
    {
        org.fdroid.fdroid.nearby.SwapWorkflowActivity.$r8$lambda$MfcA6b8Lk6hyLtjJNXNmsN0JC3I(this.f$0, p2, p3);
        return;
    }


}