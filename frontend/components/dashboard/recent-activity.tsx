import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

export function RecentActivity() {
  return (
    <div className="space-y-8">
      {[...Array(5)].map((_, i) => (
        <div className="flex items-center" key={i}>
          <Avatar className="h-9 w-9">
            <AvatarImage src={`/avatars/0${i + 1}.png`} alt="Avatar" />
            <AvatarFallback>OM</AvatarFallback>
          </Avatar>
          <div className="ml-4 space-y-1">
            <p className="text-sm font-medium leading-none">Olivia Martin</p>
            <p className="text-sm text-muted-foreground">
              Placed a bet on {["Football", "Basketball", "Tennis", "Horse Racing", "Dog Racing"][i]}
            </p>
          </div>
          <div className="ml-auto font-medium">
            +${(Math.random() * 100).toFixed(2)}
          </div>
        </div>
      ))}
    </div>
  )
}

