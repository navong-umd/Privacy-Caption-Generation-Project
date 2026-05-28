/* Application Package Name: org.fdroid.fdroid */
class PRCS_13 {
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
