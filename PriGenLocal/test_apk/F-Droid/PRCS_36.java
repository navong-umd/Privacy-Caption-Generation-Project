/*Application Package Name: org.fdroid.fdroid
class PRCS_36 {
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

/**
org.fdroid.fdroid.nearby.SwapWorkflowActivity;$r8$lambda$uDJf_7qVTjC4hWmHK9HHIiqu9fw(Lorg/fdroid/fdroid/nearby/SwapWorkflowActivity; Landroid/widget/CompoundButton; Z)V
*/

    public static synthetic void $r8$lambda$uDJf_7qVTjC4hWmHK9HHIiqu9fw(org.fdroid.fdroid.nearby.SwapWorkflowActivity p0, android.widget.CompoundButton p1, boolean p2)
    {
        p0.lambda$setUpStartVisibility$12(p1, p2);
        return;
    }

/**
org.fdroid.fdroid.nearby.SwapWorkflowActivity;onCheckedChanged(Landroid/widget/CompoundButton; Z)V
*/

    public final void onCheckedChanged(android.widget.CompoundButton p2, boolean p3)
    {
        org.fdroid.fdroid.nearby.SwapWorkflowActivity.$r8$lambda$uDJf_7qVTjC4hWmHK9HHIiqu9fw(this.f$0, p2, p3);
        return;
    }


}