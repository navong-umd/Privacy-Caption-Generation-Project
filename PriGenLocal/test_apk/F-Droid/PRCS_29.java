/*Application Package Name: org.fdroid.fdroid
class PRCS_29 {
/**
org.fdroid.fdroid.nearby.BonjourManager;onLooperPrepared()V
*/

    protected void onLooperPrepared()
    {
        try {
            org.fdroid.fdroid.nearby.BonjourManager.-$$Nest$sfputjmdns(javax.jmdns.JmDNS.create(java.net.InetAddress.getByName(org.fdroid.fdroid.FDroidApp.ipAddressString)));
            org.fdroid.fdroid.nearby.BonjourManager.-$$Nest$sfgetjmdns().addServiceListener("_http._tcp.local.", this.val$httpServiceListener);
            org.fdroid.fdroid.nearby.BonjourManager.-$$Nest$sfgetjmdns().addServiceListener("_https._tcp.local.", this.val$httpsServiceListener);
            org.fdroid.fdroid.nearby.BonjourManager.-$$Nest$sfputmulticastLock(this.val$wifiManager.createMulticastLock(this.val$context.getPackageName()));
            org.fdroid.fdroid.nearby.BonjourManager.-$$Nest$sfgetmulticastLock().setReferenceCounted(0);
            org.fdroid.fdroid.nearby.BonjourManager.-$$Nest$sfgetmulticastLock().acquire();
            org.fdroid.fdroid.nearby.BonjourManager.-$$Nest$smsendBroadcast(1, 0);
        } catch (String v0_8) {
            if (org.fdroid.fdroid.nearby.BonjourManager.-$$Nest$sfgethandler() != null) {
                org.fdroid.fdroid.nearby.BonjourManager.-$$Nest$sfgethandler().removeMessages(4151873);
                org.fdroid.fdroid.nearby.BonjourManager.-$$Nest$sfgethandler().sendMessageAtFrontOfQueue(org.fdroid.fdroid.nearby.BonjourManager.-$$Nest$sfgethandler().obtainMessage(5709));
            }
            android.util.Log.e("BonjourManager", "Error while registering jmdns service", v0_8);
            org.fdroid.fdroid.nearby.BonjourManager.-$$Nest$smsendBroadcast(65535, v0_8.getLocalizedMessage());
        }
        return;
    }


}