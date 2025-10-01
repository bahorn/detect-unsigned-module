#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("bah");
MODULE_DESCRIPTION("goat");
MODULE_VERSION("1.0");
MODULE_INFO(intree, "true");

static int mod_init(void)
{
    printk(KERN_INFO "Goat Loaded\n");
    return 0;
}

static void mod_exit(void) {
    printk(KERN_INFO "Goat Unloading\n");
}


module_init(mod_init);
module_exit(mod_exit);
