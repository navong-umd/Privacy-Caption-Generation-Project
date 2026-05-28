/* Application Package Name: org.fdroid.fdroid */
class PRCS_15 {
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


}
