/*Application Package Name: org.fdroid.fdroid
class PRCS_6 {
/**
androidx.work.impl.constraints.trackers.NetworkStateTrackerKt;getActiveNetworkState(Landroid/net/ConnectivityManager;)Landroidx/work/impl/constraints/NetworkState;
*/

    public static final androidx.work.impl.constraints.NetworkState getActiveNetworkState(android.net.ConnectivityManager p5)
    {
        int v3_0;
        kotlin.jvm.internal.Intrinsics.checkNotNullParameter(p5, "<this>");
        androidx.work.impl.constraints.NetworkState v0_4 = p5.getActiveNetworkInfo();
        int v1 = 0;
        if ((v0_4 == null) || (!v0_4.isConnected())) {
            v3_0 = 0;
        } else {
            v3_0 = 1;
        }
        boolean v4 = androidx.work.impl.constraints.trackers.NetworkStateTrackerKt.isActiveNetworkValidated(p5);
        boolean v5_1 = androidx.core.net.ConnectivityManagerCompat.isActiveNetworkMetered(p5);
        if ((v0_4 != null) && (!v0_4.isRoaming())) {
            v1 = 1;
        }
        return new androidx.work.impl.constraints.NetworkState(v3_0, v4, v5_1, v1);
    }

/**
androidx.work.impl.constraints.trackers.NetworkStateTracker24;onCapabilitiesChanged(Landroid/net/Network; Landroid/net/NetworkCapabilities;)V
*/

    public void onCapabilitiesChanged(android.net.Network p4, android.net.NetworkCapabilities p5)
    {
        kotlin.jvm.internal.Intrinsics.checkNotNullParameter(p4, "network");
        kotlin.jvm.internal.Intrinsics.checkNotNullParameter(p5, "capabilities");
        androidx.work.impl.constraints.trackers.NetworkStateTracker24 v4_3 = androidx.work.Logger.get();
        String v0_1 = androidx.work.impl.constraints.trackers.NetworkStateTrackerKt.access$getTAG$p();
        StringBuilder v1_1 = new StringBuilder();
        v1_1.append("Network capabilities changed: ");
        v1_1.append(p5);
        v4_3.debug(v0_1, v1_1.toString());
        androidx.work.impl.constraints.trackers.NetworkStateTracker24 v4_1 = this.this$0;
        v4_1.setState(androidx.work.impl.constraints.trackers.NetworkStateTrackerKt.getActiveNetworkState(androidx.work.impl.constraints.trackers.NetworkStateTracker24.access$getConnectivityManager$p(v4_1)));
        return;
    }


}